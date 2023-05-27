from django.core.files.storage import FileSystemStorage

from dynamic_storage.storage import DynamicStorageMixin


_DUMMY_CREDENTIAL = "DuMyCrEdEnTiAl"
_DUMMY_TOKEN = "DuMyCrEdEnTiAl"
_DUMMY_SECRET = "DuMyCrEdEnTiAl"


class CredentialsError(Exception):
    pass


class ASpecialFileSystemStorage(FileSystemStorage, DynamicStorageMixin):
    def __init__(self, credential):
        super(ASpecialFileSystemStorage, self).__init__()
        if credential != _DUMMY_CREDENTIAL:
            raise CredentialsError
        self.credential = credential

    def init_params(self) -> dict:
        return {"credential": self.credential}


class AnotherSpecialFileSystemStorage(FileSystemStorage, DynamicStorageMixin):
    def __init__(self, token, secret):
        super(AnotherSpecialFileSystemStorage, self).__init__()
        if token != _DUMMY_TOKEN and secret != _DUMMY_SECRET:
            raise CredentialsError
        self.token = token
        self.secret = secret

    def init_params(self) -> dict:
        return {"token": self.token, "secret": self.secret}
