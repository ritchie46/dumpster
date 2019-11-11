from model_registry.registries import base
from model_registry import file
from model_registry.model import ExampleModel


def test_init():
    mr = base.ModelRegistryBase('test')
    mr.register(ExampleModel, param='parameter')


def test_dump_and_load():
    mr = file.ModelRegistry('test')
    mr.register(ExampleModel, param='parameter')
    mr.dump('test')

    new_mr = file.ModelRegistry('test')
    new_mr.load('test')
    assert new_mr.model_.a == mr.model_.a

