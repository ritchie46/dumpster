from google.cloud import storage
import os
from dumpster.registries.storage import ModelRegistry


storage_client = storage.Client.from_service_account_json(
    os.environ["ML_PROJECT_CREDS"]
)
bucket = storage_client.get_bucket("crux-ml")

# mr = ModelRegistry('09-11-2019', bucket)
# mr.load("registry-dump/")
#
# mr.name = '10-11-2019'
# mr.dump("registry-dump/")


mr = ModelRegistry('10-11-2019', bucket)
mr.load("registry-dump/")
print(mr.model_)
# print(mr.file_source)