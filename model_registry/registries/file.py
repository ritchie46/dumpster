import os
from model_registry.registries.base import ModelRegistryBase


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

    def dump(self, dir):
        """
        Dump model source and state to disk.

        Parameters
        ----------
        dir : str
            Directory
        """
        os.makedirs(dir, exist_ok=True)
        with open(self._path(dir), "wb") as f:
            f.write(self.state_blob)

    def load(self, dir):
        """
        Load model source and state.

        Parameters
        ----------
        dir : str
            Directory
        """
        with open(self._path(dir), "rb") as f:
            self.load_blob(f)
