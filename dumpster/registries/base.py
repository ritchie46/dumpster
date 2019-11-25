import inspect
from types import ModuleType
import io
import pickle
from dumpster import utils
from dumpster.kwargs import save_kwargs_state, load_kwargs_state
from logging import getLogger
from dumpster import savers

logger = getLogger(__name__)


class ModelRegistryBase:
    """
    Utility to save model state as well as source code.
    The goal is to able to save and load a model even
    if the repositories code has changed.
    """

    def __init__(self, name):
        """
        Model Registry base class.

        Parameters
        ----------
        name : str
            Name of the model. Will be used as unique identifier.
        """
        self.name = name
        self.model_kwargs = None
        # Class source
        self.source = None
        # Source of the whole file, needed for imports of globals
        self.file_source = None
        self.model_ = None

    def _init_model(self):
        """
        Initialize the model from the source code
        and the given kwargs.
        """
        module_name = f"model_{self.name}"
        mod = ModuleType(module_name)
        mod.__dict__.update(globals())
        imports, logic = utils.split_imports_and_logic(self.file_source)

        for line in imports.splitlines():
            try:
                exec(line, mod.__dict__)
            except ModuleNotFoundError:
                pass
        exec(logic, mod.__dict__)
        exec(self.source, mod.__dict__)

        key = utils.get_class_name(self.source)
        model_class = mod.__dict__[key]
        self.model_ = model_class(**self.model_kwargs)

    def register(self, obj, add_save=None, **kwargs):
        """
        Register a Model class.

        Parameters
        ----------
        obj : class
            Model class definition. Model should have save and load method.
        add_save : str
            Add save method to class source.
                - 'pytorch'
        kwargs : kwargs
            Keyword arguments used to initialize the model.
        """
        self.source = utils.clean_source(inspect.getsource(obj))

        if add_save is not None:
            self.source += getattr(savers, add_save)

        with open(inspect.getabsfile(obj)) as f:
            self.file_source = f.read()
        self.model_kwargs = kwargs
        if inspect.isclass(obj):
            self._init_model()
        else:
            self.model_ = obj

    @property
    def state_blob_f(self):
        f = io.BytesIO()
        self.model_.save(f)
        f.seek(0)

        blob = io.BytesIO()
        pickle.dump(
            {
                "source": self.source,
                "file_source": self.file_source,
                "model_blob": f.read(),
                "model_kwargs": save_kwargs_state(self.model_kwargs),
            },
            blob,
        )
        blob.seek(0)
        return blob

    @property
    def state_blob(self):
        return self.state_blob_f.read()

    def load_blob(self, blob):
        d = pickle.load(blob)
        self.__dict__.update({k: v for k, v in d.items() if k != "model_blob"})
        self.model_kwargs = load_kwargs_state(self.model_kwargs)
        self._init_model()
        f = io.BytesIO(d["model_blob"])
        self.model_.load(f)

