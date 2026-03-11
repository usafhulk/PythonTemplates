"""DI Container Tests."""
import pytest
from ..core import DIContainer


class IService:
    pass


class ConcreteService(IService):
    def hello(self) -> str:
        return "hello"


def test_register_and_resolve():
    container = DIContainer()
    container.register(IService, ConcreteService)
    service = container.resolve(IService)
    assert isinstance(service, ConcreteService)
    assert service.hello() == "hello"


def test_singleton_behavior():
    container = DIContainer()
    container.register(IService, ConcreteService, singleton=True)
    s1 = container.resolve(IService)
    s2 = container.resolve(IService)
    assert s1 is s2


def test_register_instance():
    container = DIContainer()
    instance = ConcreteService()
    container.register_instance(IService, instance)
    resolved = container.resolve(IService)
    assert resolved is instance


def test_missing_registration_raises():
    container = DIContainer()
    with pytest.raises(KeyError):
        container.resolve(IService)
