from dumpster.registries.base import ModelRegistryBase
from dumpster import storage
import io


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

    def dump(self, key):
        """
        Save model state and source.

        Parameters
        ----------
        key : str
            Location key in gcp storage
        """
        storage.write_blob(key, self.state_blob, self.bucket)

    def load(self, key):
        """
        Load model state and source.

        Parameters
        ----------
        key : str
            Location key in gcp storage
        """
        f = io.BytesIO()
        storage.download_blob(key, f, self.bucket)
        f.seek(0)
        self.load_blob(f)
