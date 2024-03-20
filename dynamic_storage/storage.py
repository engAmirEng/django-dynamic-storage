from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.module_loading import import_string


class prob(TypedDict):
    constructor: dict
    import_path: str


class AbstractBaseStorageDispatcher(ABC):
    def __new__(cls, constructor: dict, **kwargs):
        return cls.get_storage(**constructor)

    @staticmethod
    @abstractmethod
    def get_storage(**kwargs) -> DynamicStorage: ...


class DynamicStorageMixin(ABC):
    @abstractmethod
    def init_params(self) -> dict:
        """parameters that are passed to get_storage method of your STORAGE_DISPATCHER"""
        ...

    def __eq__(self, other) -> bool:
        """
        how to differentiate two instances of the same storage class
        Override this for your use case,
        for example add the comparison based on bucket names
        """
        return (
            self.__class__ == other.__class__
            and self.init_params() == other.init_params()
        )

    def uninit(self) -> prob:
        """get the required properties for future initialization"""
        return {
            "import_path": f"{self.__class__.__module__}.{self.__class__.__qualname__}",
            "constructor": self.init_params(),
        }

    @classmethod
    def init(cls, probs: prob) -> DynamicStorageMixin:
        """initialize storage"""
        StorageDispatcher = import_string(settings.STORAGE_DISPATCHER)
        return StorageDispatcher(
            constructor=probs["constructor"], import_path=probs["import_path"]
        )


class DynamicStorage(DynamicStorageMixin, Storage): ...
