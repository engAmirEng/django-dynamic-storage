from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from django.core.files.storage import Storage


# {"import_path": str, "constructor": dict}
prob = Dict[str, Any]


class DynamicStorageMixin(ABC):
    @abstractmethod
    def init_params(self) -> dict:
        """parameters for calling __init__ on storage class"""
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
        module_name = ".".join(probs["import_path"].split(".")[:-1])
        class_name = probs["import_path"].split(".")[-1]
        StorageClass: Callable = getattr(
            importlib.import_module(module_name), class_name
        )
        return StorageClass(**probs["constructor"])


class DynamicStorage(DynamicStorageMixin, Storage):
    ...
