from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

from dynamic_storage.storage import DynamicStorageMixin


_DUMMY_CREDENTIAL = "DuMyCrEdEnTiAl"
_DUMMY_TOKEN = "DuMyCrEdEnTiAl"
_DUMMY_SECRET = "DuMyCrEdEnTiAl"


class CredentialsError(Exception):
    pass


@deconstructible
class ASpecialFileSystemStorage(FileSystemStorage, DynamicStorageMixin):
    def __init__(self, credential):
        super(ASpecialFileSystemStorage, self).__init__()
        if credential != _DUMMY_CREDENTIAL:
            raise CredentialsError
        self.credential = credential

    def init_params(self) -> dict:
        return {
            "identifier": "special_file_system_storage",
            "credential": self.credential,
        }


@deconstructible
class AnotherSpecialFileSystemStorage(FileSystemStorage, DynamicStorageMixin):
    def __init__(self, token, secret):
        super(AnotherSpecialFileSystemStorage, self).__init__()
        if token != _DUMMY_TOKEN and secret != _DUMMY_SECRET:
            raise CredentialsError
        self.token = token
        self.secret = secret

    def init_params(self) -> dict:
        return {
            "identifier": "another_special_fileSystem_storage",
            "token": self.token,
            "secret": self.secret,
        }
