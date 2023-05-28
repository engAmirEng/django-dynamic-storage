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
class TestPreDynamicFileSaveSignal:
    def test_when_no_destination_storage_is_set(
        self, file_model_obj_loaded, register_signal
    ):
        file_model_obj_loaded.save()

        obj = FileModel.objects.get()
        assert obj.file1.storage.__class__ == ASpecialFileSystemStorage
        assert obj.file2.storage.__class__ == AnotherSpecialFileSystemStorage

    def test_priority(self, file_model_obj_loaded, register_signal):
        file_model_obj_loaded.file1.destination_storage = (
            AnotherSpecialFileSystemStorage(_DUMMY_TOKEN, _DUMMY_SECRET)
        )
        file_model_obj_loaded.file2.destination_storage = ASpecialFileSystemStorage(
            _DUMMY_CREDENTIAL
        )
        file_model_obj_loaded.save()

        obj = FileModel.objects.get()
        assert obj.file1.storage.__class__ == ASpecialFileSystemStorage
        assert obj.file2.storage.__class__ == AnotherSpecialFileSystemStorage
