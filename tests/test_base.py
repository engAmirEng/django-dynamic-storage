import pytest
from tests.testapp.models import FileModel

from dynamic_storage.test.storage import (
    _DUMMY_CREDENTIAL,
    _DUMMY_SECRET,
    _DUMMY_TOKEN,
    AnotherSpecialFileSystemStorage,
    ASpecialFileSystemStorage,
)


@pytest.mark.django_db
class TestBase:
    def test_explicit_destination_storage_set(self, file_model_obj_loaded):
        file_model_obj_loaded.file1.destination_storage = ASpecialFileSystemStorage(
            _DUMMY_CREDENTIAL
        )
        file_model_obj_loaded.file2.destination_storage = (
            AnotherSpecialFileSystemStorage(_DUMMY_TOKEN, _DUMMY_SECRET)
        )
        file_model_obj_loaded.save()

        obj = FileModel.objects.get()
        assert obj.file1.storage.__class__ == ASpecialFileSystemStorage
        assert obj.file2.storage.__class__ == AnotherSpecialFileSystemStorage

    def test_explicit_save_storage_set(self, file_model_obj_loaded):
        file_model_obj_loaded.file1.save(
            file_model_obj_loaded.file1.name,
            file_model_obj_loaded.file1.file,
            storage=ASpecialFileSystemStorage(_DUMMY_CREDENTIAL),
            save=False,
        )
        file_model_obj_loaded.file2.save(
            file_model_obj_loaded.file2.name,
            file_model_obj_loaded.file2.file,
            storage=(AnotherSpecialFileSystemStorage(_DUMMY_TOKEN, _DUMMY_SECRET)),
            save=False,
        )
        file_model_obj_loaded.save()

        obj = FileModel.objects.get()
        assert obj.file1.storage.__class__ == ASpecialFileSystemStorage
        assert obj.file2.storage.__class__ == AnotherSpecialFileSystemStorage

    def test_cannot_change_the_storage(self, file_model_obj_loaded):
        file_model_obj_loaded.file1.destination_storage = ASpecialFileSystemStorage(
            _DUMMY_CREDENTIAL
        )
        file_model_obj_loaded.file2.destination_storage = (
            AnotherSpecialFileSystemStorage(_DUMMY_TOKEN, _DUMMY_SECRET)
        )
        file_model_obj_loaded.save()
        obj = FileModel.objects.get()
        obj.file1.destination_storage = AnotherSpecialFileSystemStorage(
            _DUMMY_TOKEN, _DUMMY_SECRET
        )
        with pytest.raises(AssertionError):
            obj.file1.save(obj.file1.name, obj.file1.file)
        obj.file1.destination_storage = ASpecialFileSystemStorage(_DUMMY_CREDENTIAL)
        obj.file1.save(obj.file1.name, obj.file1.file)
