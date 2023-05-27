import os

import pytest
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.dispatch import receiver
from tests.testapp.models import FileModel, ImageModel

from PIL import Image

from dynamic_storage.models import DynamicFieldFile
from dynamic_storage.signals import pre_dynamic_file_save
from dynamic_storage.storage import DynamicStorage
from dynamic_storage.test.storage import (
    _DUMMY_CREDENTIAL,
    _DUMMY_SECRET,
    _DUMMY_TOKEN,
    AnotherSpecialFileSystemStorage,
    ASpecialFileSystemStorage,
)


@pytest.fixture
def file_model_obj_loaded():
    file_model_obj = FileModel()
    file_model_obj.file1 = ContentFile(b"test_explicit_save_file1", name="file1.txt")
    file_model_obj.file2 = ContentFile(b"test_explicit_save_file2", name="file2.txt")
    yield file_model_obj
    if file_model_obj.pk:
        file_model_obj.delete()


@pytest.fixture
def image_model_obj_loaded():
    file_model_obj = ImageModel()

    image1 = Image.new("RGB", (400, 300))
    image1_path = os.path.join(settings.MEDIA_ROOT, "image1.jpg")
    image1.save(image1_path)
    image2 = Image.new("RGB", (800, 600))
    image2_path = os.path.join(settings.MEDIA_ROOT, "image2.jpg")
    image2.save(image2_path)
    with open(image1_path, "rb") as i1, open(image2_path, "rb") as i2:
        file_model_obj.image1 = SimpleUploadedFile(
            "test_image1.jpg", content=i1.read(), content_type="image/jpeg"
        )
        file_model_obj.image2 = SimpleUploadedFile(
            "test_image2.jpg", content=i2.read(), content_type="image/jpeg"
        )

    yield file_model_obj
    if file_model_obj.pk:
        file_model_obj.delete()


@pytest.fixture
def register_signal():
    @receiver(pre_dynamic_file_save, sender=FileModel)
    def set_storages_for_file1_file2(
        instance: FileModel,
        field_file: DynamicFieldFile,
        to_storage: DynamicStorage,
        *args,
        **kwargs
    ):
        instance.file1.destination_storage = ASpecialFileSystemStorage(
            _DUMMY_CREDENTIAL
        )
        instance.file2.destination_storage = AnotherSpecialFileSystemStorage(
            _DUMMY_TOKEN, _DUMMY_SECRET
        )

    yield
    pre_dynamic_file_save.disconnect(set_storages_for_file1_file2)
