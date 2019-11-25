from dumpster.registries import base
from dumpster import file
from dumpster.model import ExampleModel
import io
import pytest


def test_init():
    mr = base.ModelRegistryBase("test")
    mr.register(ExampleModel, param="parameter")


def test_dump_and_load():
    mr = file.ModelRegistry("test")
    mr.register(ExampleModel, param="parameter")
    mr.dump("test")

    new_mr = file.ModelRegistry("test")
    new_mr.load("test")
    assert new_mr.model_.a == mr.model_.a


def test_dump_and_load_bytesio():
    mr = file.ModelRegistry("test")
    mr.register(ExampleModel, param="parameter")
    f = io.BytesIO()
    mr.dump(f)
    f.seek(0)

    new_mr = file.ModelRegistry("test")
    new_mr.load(f)
    assert new_mr.model_.a == mr.model_.a


def test_add_dump_methods():
    mr = file.ModelRegistry("test")
    mr.register(ExampleModel, insert_methods="pytorch", param="parameter")

    assert hasattr(mr.model_, "save")
    assert hasattr(mr.model_, "load")

    # Pytorch save method calls self.state_dict, which doesn't exist.
    with pytest.raises(AttributeError):
        f = io.BytesIO()
        mr.model_.save(f)
