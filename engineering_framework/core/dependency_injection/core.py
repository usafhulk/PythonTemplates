"""Dependency Injection Core."""
import inspect
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from .interfaces import Container

logger = logging.getLogger(__name__)
T = TypeVar("T")

_signature_cache: Dict[type, inspect.Signature] = {}


def _get_signature(cls: type) -> inspect.Signature:
    """Return (and cache) the __init__ signature for a class."""
    if cls not in _signature_cache:
        _signature_cache[cls] = inspect.signature(cls.__init__)
    return _signature_cache[cls]


class DIContainer(Container):
    """Lightweight DI container with constructor injection."""

    def __init__(self) -> None:
        self._registrations: Dict[type, Any] = {}
        self._singletons: Dict[type, Any] = {}
        self._singleton_flags: Dict[type, bool] = {}

    def register(self, interface: Type[T], implementation: Any, singleton: bool = True) -> None:
        self._registrations[interface] = implementation
        self._singleton_flags[interface] = singleton
        logger.debug("Registered %s -> %s (singleton=%s)", interface.__name__, implementation, singleton)

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-built instance."""
        self._singletons[interface] = instance
        self._singleton_flags[interface] = True

    def resolve(self, interface: Type[T]) -> T:
        if interface in self._singletons:
            return self._singletons[interface]  # type: ignore[return-value]
        if interface not in self._registrations:
            raise KeyError(f"No registration found for {interface}")
        impl = self._registrations[interface]
        if callable(impl) and not isinstance(impl, type):
            instance = impl()
        elif isinstance(impl, type):
            instance = self._build(impl)
        else:
            instance = impl
        if self._singleton_flags.get(interface, True):
            self._singletons[interface] = instance
        return instance  # type: ignore[return-value]

    def _build(self, cls: type) -> Any:
        sig = _get_signature(cls)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name == "self":
                continue
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[name] = self.resolve(param.annotation)
                except KeyError:
                    if param.default == inspect.Parameter.empty:
                        raise
        return cls(**kwargs)
