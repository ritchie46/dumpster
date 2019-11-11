from dumpster.registries import base
from dumpster import file
from dumpster.model import ExampleModel
import io


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
