import pytest
from tests.testapp.models import ImageModel

from dynamic_storage.test.storage import (
    _DUMMY_CREDENTIAL,
    _DUMMY_SECRET,
    _DUMMY_TOKEN,
    AnotherSpecialFileSystemStorage,
    ASpecialFileSystemStorage,
)


@pytest.mark.django_db
class TestImageField:
    def test_dimentions(self, image_model_obj_loaded):
        image_model_obj_loaded.image1.destination_storage = ASpecialFileSystemStorage(
            _DUMMY_CREDENTIAL
        )
        image_model_obj_loaded.image2.destination_storage = (
            AnotherSpecialFileSystemStorage(_DUMMY_TOKEN, _DUMMY_SECRET)
        )
        image_model_obj_loaded.save()

        obj = ImageModel.objects.get()
        assert (
            obj.image1.width == 400
            and obj.image1.height == 300
            and obj.image2.width == 800
            and obj.image2.height == 600
        )
