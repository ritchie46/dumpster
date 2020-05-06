import io
import os
from dumpster.registries.base import ModelRegistryBase


class ModelRegistry(ModelRegistryBase):
    """
    Utility to save model state as well as source code.
    The goal is to able to save and load a model even
    if the repositories code has changed.
    """

    def __init__(self, name=None):
        super().__init__(name)

    def _path(self, dir):
        """
        Get path where model state is pickled.
        The final path is `dir`/`name`.pth

        Parameters
        ----------
        dir : str
            Save/load directory

        Returns
        -------
        path : str

        """
        return os.path.join(dir, f"{self.name}.pth")

    def dump(self, path):
        """
        Dump model source and state to disk.

        Parameters
        ----------
        path : Union[str, file]
            Directory name
        """
        if isinstance(path, str):
            if path.lower().endswith((".pth", ".pkl")):
                func = lambda x: x
            else:
                os.makedirs(path, exist_ok=True)
                func = self._path
            with open(func(path), "wb", encoding="utf-8") as f:
                f.write(self.state_blob)
        else:
            path.write(self.state_blob)
        return self

    def load(self, path, expand_path=True):
        """
        Load model source and state.

        Parameters
        ----------
        path : Union[str, file]
            Directory name
        expand_path : bool
            Assumes given path is a directory and searches
            for ModelRegistry file. If False, assumes path is model file.
        """
        if isinstance(path, str):
            if path.lower().endswith((".pth", ".pkl")):
                expand_path = False

            if expand_path:
                func = self._path
            else:
                func = lambda x: x
            with open(func(path), "rb", encoding="utf-8") as f:
                self.load_blob(f)
        else:
            if not isinstance(path, (io.BytesIO, io.BufferedReader)):
                raise ValueError("File object should read as bytes not text.")
            self.load_blob(path)
        return self
