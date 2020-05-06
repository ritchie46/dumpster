import inspect
from types import ModuleType
import io
import pickle
from dumpster import utils
import re


class CodeInspector:
    def __init__(self, name):
        self.name = name
        # Class source
        self.source = None
        # Source of the whole file, needed for imports of globals
        self.file_source = None
        self.module = ModuleType(self.name)
        self.module.__dict__.update(globals())

    def load(self):
        """
        Execute the defined source code
        """

        imports, logic = utils.split_imports_and_logic(self.file_source)

        # If imports are not possible, skip
        for line in imports.splitlines():
            try:
                exec(line, self.module.__dict__)
            except ModuleNotFoundError:
                pass

        # If some lines are undefined in the namespace of the source file
        # These lines are trimmed. Maybe it works. Fingers crossed.
        loaded = False
        while not loaded:
            try:
                exec(logic, self.module.__dict__)
                loaded = True
            except NameError as e:
                g = re.search(r"name '(\w+)' is not defined", str(e))
                if g:
                    logic = utils.filter_lines_containing(logic, g.group(1))
                else:
                    # Will probably fail
                    loaded = True

        exec(logic, self.module.__dict__)
        exec(self.source, self.module.__dict__)

    def register(self, obj):
        """
        Register a Class.

        Parameters
        ----------
        obj : class/ function
        """
        try:
            self.source = utils.clean_source(inspect.getsource(obj))
            with open(inspect.getabsfile(obj), encoding="utf-8") as f:
                self.file_source = f.read()
        except TypeError:  # built-in class
            return False
        return True

    @property
    def state_blob_f(self):
        blob = io.BytesIO()
        pickle.dump(
            {"source": self.source, "file_source": self.file_source,}, blob,
        )
        blob.seek(0)
        return blob

    @property
    def state_blob(self):
        return self.state_blob_f.read()

    def load_blob(self, blob):
        d = pickle.loads(blob)
        self.__dict__.update(d)
        self.load()
