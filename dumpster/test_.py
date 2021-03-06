import os
from dumpster import utils
from dumpster.registries import base
from dumpster import file
from dumpster.model import ExampleModel, ExampleModelBare
import io
import pytest


@pytest.fixture(scope="module")
def files_dir(tmpdir_factory):
    return tmpdir_factory.mktemp("test_dir")


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


def test_load_model_source():
    mr = file.ModelRegistry("test")
    with open(os.path.join(os.path.dirname(__file__), "test/test.pth"), "rb") as f:
        assert isinstance(mr.load_model_source(f), str)


def test_time_hash():
    assert len(utils.get_time_hash(6)) == 6


def test_raise():
    mr = file.ModelRegistry("test")
    with pytest.raises(ValueError):
        mr.register(ExampleModelBare, param="parameter")


def test_pickle_insert(files_dir):
    path = str(files_dir.join("dump.pkl"))
    mr = file.ModelRegistry("test")
    mr.register(ExampleModelBare, insert_methods="pickle", param="parameter")
    mr.dump(path)

    # create new MR
    mr_ = file.ModelRegistry("test")
    mr_.load(path)
    assert type(mr.model_.a) == type(mr_.model_.a)


def test_prevent_init_execution():
    src = """
class ExampleModelBare:
    def __init__(self, param):
        self.a = config.Command
        self.param = param
    """

    assert utils.monkeypatch_init(src) == """
class ExampleModelBare:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        return None
        self.a = config.Command
        self.param = param
    """


def test_jit_register(files_dir):
    path = str(files_dir.join("dump.pkl"))

    model = ExampleModelBare("parameter")
    mr = file.ModelRegistry("test")
    mr.register(model, insert_methods='pickle')
    mr.dump(path)

    # create new MR
    mr_ = file.ModelRegistry("test")
    mr_.load(path)
    assert type(mr.model_.a) == type(mr_.model_.a)