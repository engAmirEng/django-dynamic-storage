from typing import Dict, Any

from django.db import models
from django.db.models.fields.files import (
    FieldFile,
    FileDescriptor,
    ImageField,
    ImageFieldFile,
    ImageFileDescriptor,
)
from django.utils.translation import gettext_lazy as _

from say.dynamic_storage.storage import Storage, prob

# {"name": str, "storage": prob}
jsonfield = Dict[str, Any]


class DynamicFieldFile(FieldFile):
    def __init__(self, instance, field, name, storage: Storage = None):
        super(DynamicFieldFile, self).__init__(instance, field, name)
        self.current_storage = storage
        self.storage = storage or self.storage

    def dictionary(self) -> jsonfield:
        """Value to be stored in JSONField"""
        return {"name": str(self), "storage": self.storage.uninit()}

    def save(self, name, content, storage: Storage = None, save=True):
        """This is the dynamic storage save"""
        assert self.current_storage == storage if self.current_storage else True
        if storage:
            self.storage = storage
        super(DynamicFieldFile, self).save(name, content, save=save)


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
            storage = Storage.init(storage_prob) if storage_prob else storage_prob
            attr = self.field.attr_class(
                instance, self.field, file.get("name"), storage
            )
            instance.__dict__[self.field.attname] = attr

        return instance.__dict__[self.field.attname]


class DynamicFileField(models.JSONField, models.FileField):
    """FileField with json db representation that contain info for dynamic behavior"""

    attr_class = DynamicFieldFile

    descriptor_class = DynamicFileDescriptor

    def get_prep_value(self, value):
        if value is None:
            return value
        if not isinstance(value, dict):
            value = value.dictionary()
        return models.JSONField.get_prep_value(self, value)

    def formfield(self, **kwargs):
        return models.FileField.formfield(self, **kwargs)

    def validate(self, value, model_instance):
        super(DynamicFileField, self).validate(value.dictionary(), model_instance)


class DynamicImageFieldFile(ImageFieldFile, DynamicFieldFile):
    pass


class DynamicImageFileDescriptor(ImageFileDescriptor, DynamicFileDescriptor):
    pass


class DynamicImageField(ImageField, DynamicFileField):
    """ImageField with json db representation that contain info for dynamic behavior"""

    attr_class = DynamicImageFieldFile
    descriptor_class = DynamicImageFileDescriptor
