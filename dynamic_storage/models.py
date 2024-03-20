from typing import Any, Dict

import django
from django.db import models
from django.db.models.fields.files import (
    FieldFile,
    FileDescriptor,
    ImageField,
    ImageFieldFile,
    ImageFileDescriptor,
)

from .signals import pre_dynamic_file_save
from .storage import DynamicStorage, prob


if django.VERSION >= (3, 1):
    from django.db.models import JSONField
else:
    from django.contrib.postgres.fields import JSONField

# {"name": str, "storage": prob}
jsonfield = Dict[str, Any]


class DynamicFieldFile(FieldFile):
    def __init__(self, instance, field, name, storage: DynamicStorage = None):
        super(DynamicFieldFile, self).__init__(instance, field, name)
        self._current_storage = (
            storage  # keep track of the storage the file is actually at
        )
        self.storage = storage or self.storage

        # To be able to save the file to the appropriate storage
        # if providing the save() method with storage argument is not possible
        self.destination_storage = None

    def dictionary(self) -> jsonfield:
        """Value to be stored in JSONField"""
        return {"name": str(self), "storage": self.storage.uninit()}

    def save(self, name, content, /, storage: DynamicStorage = None, save=True):
        """
        This is the dynamic storage save
        """
        self.destination_storage = storage or self.destination_storage
        # Ensure we are not trying to move obj between storages (yet)
        assert (
            self._current_storage == self.destination_storage
            if self._current_storage
            else True
        ), (
            f"{self.instance}'s file is saved at {str(self._current_storage)} but the `destination_storage`"
            f" is set to {str(self.destination_storage)} wile moving is not supported yet."
        )

        pre_dynamic_file_save.send(
            sender=self.instance.__class__,
            instance=self.instance,
            field_file=self,
            to_storage=self.destination_storage,
        )

        storage = self.destination_storage or self._current_storage or self.storage

        name = self.field.generate_filename(self.instance, name)
        self.name = storage.save(name, content, max_length=self.field.max_length)
        self.storage = self._current_storage = self.destination_storage = storage

        # This is the replacement for 'setattr(self.instance, self.field.attname, self.name)'
        # because instance is not wrote to db yet, reinstantiating will break setting the right storage
        getattr(self.instance, self.field.attname).name = self.name

        self._committed = True

        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()

    def __getstate__(self):
        # Don't know how to get the state related to storage
        raise NotImplementedError

    def __setstate__(self, state):
        # __getstate__ is not implemented
        raise NotImplementedError


class DynamicFileDescriptor(FileDescriptor):
    def __get__(self, instance, cls=None):
        file = super(DynamicFileDescriptor, self).__get__(instance, cls=cls)
        # If this value is a dictionary (instance.file = {"name": "path/to/file", **kw}) or {}
        # then we simply wrap it with the appropriate attribute class according
        # to the file field. [This is DynamicFieldFile for DynamicFileField and
        # ImageFieldFile for ImageFields; it's also conceivable that user
        # subclasses might also want to subclass the attribute class]. This
        # object understands how to convert a jsonfield to a file, and also how to
        # handle dict().
        if isinstance(file, dict):
            storage_prob: prob = file.get("storage")
            storage = (
                DynamicStorage.init(storage_prob, instance=instance, field=self.field)
                if storage_prob
                else storage_prob
            )
            attr = self.field.attr_class(
                instance, self.field, file.get("name"), storage
            )
            instance.__dict__[self.field.attname] = attr

        return instance.__dict__[self.field.attname]


class DynamicFileField(JSONField, models.FileField):
    """FileField with json db representation that contain info for dynamic behavior"""

    attr_class = DynamicFieldFile

    descriptor_class = DynamicFileDescriptor

    call_prep_or_db_pred = (
        "db_prep" if (4, 2, 0) <= django.VERSION[:3] < (4, 2, 2) else "prep"
    )

    def get_prep_value(self, value):
        if self.call_prep_or_db_pred == "prep":
            if value is None:
                return value
            if not isinstance(value, dict):
                value = value.dictionary()
            return JSONField.get_prep_value(self, value)
        return super(DynamicFileField, self).get_prep_value(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if self.call_prep_or_db_pred == "db_prep":
            if value is None:
                return value
            if not isinstance(value, dict):
                value = value.dictionary()
        return super(DynamicFileField, self).get_db_prep_value(
            value, connection, prepared
        )

    def formfield(self, **kwargs):
        return models.FileField.formfield(self, **kwargs)

    def validate(self, value, model_instance):
        super(DynamicFileField, self).validate(value.dictionary(), model_instance)


class DynamicImageFieldFile(ImageFieldFile, DynamicFieldFile):
    def save(self, *args, **kwargs):
        super(DynamicImageFieldFile, self).save(*args, **kwargs)
        # Since reinstantiating the FieldFile after calling save() is not the case anymore
        # (due to delete 'setattr(self.instance, self.field.attname, self.name)')
        self.field.update_dimension_fields(self.instance, force=True)


class DynamicImageFileDescriptor(ImageFileDescriptor, DynamicFileDescriptor):
    pass


class DynamicImageField(ImageField, DynamicFileField):
    """ImageField with json db representation that contain info for dynamic behavior"""

    attr_class = DynamicImageFieldFile
    descriptor_class = DynamicImageFileDescriptor
