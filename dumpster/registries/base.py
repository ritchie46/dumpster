import inspect
from types import ModuleType
import io
import pickle
from dumpster.utils import clean_source, get_class_name


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
        exec(self.file_source, mod.__dict__)
        exec(self.source, mod.__dict__)

        key = get_class_name(self.source)
        model_class = mod.__dict__[key]
        self.model_ = model_class(**self.model_kwargs)

    def register(self, obj, **kwargs):
        """
        Register a Model class inherited from autotrain.model.model.BaseModel

        Parameters
        ----------
        obj : class
            Model class definition. Model should have save and load method.
        kwargs : kwargs
            Keyword arguments used to initialize the model.
        """
        self.source = clean_source(inspect.getsource(obj))
        with open(inspect.getabsfile(obj)) as f:
            self.file_source = f.read()
        self.model_kwargs = kwargs
        self._init_model()

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
                "model_kwargs": self.model_kwargs,
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
        self._init_model()
        f = io.BytesIO(d["model_blob"])
        self.model_.load(f)
