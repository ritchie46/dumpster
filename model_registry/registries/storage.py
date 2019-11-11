from model_registry.registries.base import ModelRegistryBase
from model_registry import storage
import io


class ModelRegistry(ModelRegistryBase):
    def __init__(self, name, bucket):
        super().__init__(name)
        self.bucket = bucket

    def _path(self):
        return f"registry-dump/{self.name}.pth"

    def dump(self):
        storage.write_blob(self._path(), self.state_blob, self.bucket)

    def load(self):
        f = io.BytesIO()
        storage.download_blob(self._path(), f, self.bucket)
        f.seek(0)
        self.load_blob(f)
