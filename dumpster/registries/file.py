import os
from dumpster.registries.base import ModelRegistryBase


class ModelRegistry(ModelRegistryBase):
    """
    Utility to save model state as well as source code.
    The goal is to able to save and load a model even
    if the repositories code has changed.
    """

    def __init__(self, name):
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
            os.makedirs(path, exist_ok=True)
            with open(self._path(path), "wb") as f:
                f.write(self.state_blob)
        else:
            path.write(self.state_blob)

    def load(self, path):
        """
        Load model source and state.

        Parameters
        ----------
        path : Union[str, file]
            Directory name
        """
        if isinstance(path, str):
            with open(self._path(path), "rb") as f:
                self.load_blob(f)
        else:
            self.load_blob(path)
