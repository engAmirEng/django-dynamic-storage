from dynamic_storage.storage import AbstractBaseStorageDispatcher, DynamicStorage
from dynamic_storage.test.storage import (
    AnotherSpecialFileSystemStorage,
    ASpecialFileSystemStorage,
)


class MyStorageDispatcher(AbstractBaseStorageDispatcher):
    @staticmethod
    def get_storage(**kwargs):
        if kwargs.get("identifier") == "special_file_system_storage":
            return ASpecialFileSystemStorage(credential=kwargs["credential"])
        elif kwargs.get("identifier") == "another_special_fileSystem_storage":
            return AnotherSpecialFileSystemStorage(
                token=kwargs["token"], secret=kwargs["secret"]
            )
        raise NotImplementedError
