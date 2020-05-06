import inspect
from types import ModuleType
import io
import pickle
from dumpster import utils
from dumpster.kwargs import save_kwargs_state, load_kwargs_state
from logging import getLogger
from dumpster import dump_methods

logger = getLogger(__name__)


def check_validity(mr):
    valid = hasattr(mr, "save") and hasattr(mr, "load")
    if not valid:
        raise ValueError(
            "Could not find any load or save method. Implement these or set the 'insert_methods' argument."
        )


class ModelRegistryBase:
    """
    Utility to save model state as well as source code.
    The goal is to able to save and load a model even
    if the repositories code has changed.
    """

    def __init__(self, name=None):
        """
        Model Registry base class.

        Parameters
        ----------
        name : str
            Name of the model. Will be used as unique identifier.
        """
        self.name = utils.get_time_hash(6) if name is None else name
        self.model_kwargs = None
        # Class source
        self.source = None
        # Source of the whole file, needed for imports of globals
        self.file_source = None
        self.model_ = None
        self.cls = None
        self._insert_methods = "none"

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
            except ModuleNotFoundError as e:
                logger.warning(
                    f"Could not import {e.name}. If you cannot load model, add this to sys.path."
                )
        exec(logic, mod.__dict__)
        exec(self.source, mod.__dict__)

        key = utils.get_class_name(self.source)
        model_class = mod.__dict__[key]
        self.model_ = model_class(**self.model_kwargs)

    def register(self, obj, insert_methods="none", init_model=True, **kwargs):
        """
        Register a Model class.

        Parameters
        ----------
        obj : class
            Model class definition. Model should have save and load method.
        insert_methods : str
            Insert required 'save' and 'load' method to class source.
                - 'none'
                - 'pytorch'
        init_model : bool
            Initiate the model from source.
        kwargs : kwargs
            Keyword arguments used to initialize the model.
        """
        if inspect.isclass(obj):
            self.cls = obj
        else:
            self.cls = type(obj)
        self.source = utils.clean_source(inspect.getsource(self.cls))
        self.source += getattr(dump_methods, insert_methods)

        file_path = inspect.getabsfile(self.cls)
        with open(file_path, encoding="utf-8") as f:
            self.file_source = f.read()

        self.model_kwargs = kwargs
        if not inspect.isclass(obj):
            self.source = utils.monkeypatch_init(self.source)
            self.model_kwargs = obj.__dict__
        if init_model:
            self._init_model()

            # self.model_ = obj
        check_validity(self.model_)

    @property
    def state_blob_f(self):
        f = io.BytesIO()
        self.model_.save(f)
        f.seek(0)

        blob = io.BytesIO()
        pickle.dump(
            {
                "source": self.source,
                "cls": self.cls,
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

    def load_blob(self, f):
        """
        Loads source, attributes and model instance.

        Parameters
        ----------
        f : file
        """
        # Starts with the base source code and tries to load it.
        # If that doesn't succeed, other dump_methods are tried.
        for a in filter(lambda v: not v.startswith("__"), dir(dump_methods)):
            try:
                d = self._load_source(f)
                self.source += getattr(dump_methods, a)
                self._init_model()
                f = io.BytesIO(d["model_blob"])
                self.model_.load(f)
                break
            except Exception:
                pass

    def _load_source(self, f):
        """
        Only load source and attributes. Does not instantiate the model instance.

        Parameters
        ----------
        f : file
        """
        d = pickle.load(f)
        self.__dict__.update({k: v for k, v in d.items() if k != "model_blob"})
        self.model_kwargs = load_kwargs_state(self.model_kwargs)
        return d

    def load_model_source(self, f):
        """

        Parameters
        ----------
        f : file

        Returns
        -------

        """
        self._load_source(f)
        return self.file_source

    def update_source(self):
        """
        Use current repositories source (loaded from self.cls) to load the model.
        """
        model_kwargs = self.model_kwargs
        self.register(self.cls, insert_methods=self._insert_methods, init_model=False)
        self.model_kwargs = model_kwargs
        self.load_blob(self.state_blob_f)
