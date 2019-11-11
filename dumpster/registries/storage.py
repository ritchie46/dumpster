from dumpster.registries.base import ModelRegistryBase
from dumpster import storage
import io
import os


class ModelRegistry(ModelRegistryBase):
    def __init__(self, name, bucket):
        """
        Save model to google cloud storage.

        Parameters
        ----------
        name : str
            Name of the model. Will be used as unique identifier.
        bucket : google.cloud.storage.bucket.Bucket
            Google storage bucket.
        """
        super().__init__(name)
        self.bucket = bucket

    def _path(self, key):
        """
        If path path with extension is given, does nothing.

        If no extension was given. The last path location
        in the key will be interpreted as directory.
        Will return `some/directory/<name>.pth`

        Parameters
        ----------
        key : str
            Location key in gcp storage
        Returns
        -------
        key : str

        """
        _, ext = os.path.splitext(key)
        if len(ext) == 0:
            return os.path.join(key, f"{self.name}.pth")
        else:
            return key

    def dump(self, key):
        """
        Save model state and source.

        Parameters
        ----------
        key : str
            Location key in gcp storage
        """
        storage.write_blob(self._path(key), self.state_blob_f, self.bucket)

    def load(self, key):
        """
        Load model state and source.

        Parameters
        ----------
        key : str
            Location key in gcp storage
        """
        f = io.BytesIO()
        storage.download_blob(self._path(key), f, self.bucket)
        f.seek(0)
        self.load_blob(f)
