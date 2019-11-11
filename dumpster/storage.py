def read_blob(blob, bucket):
    return bucket.blob(blob).download_as_string().decode("utf-8", errors="ignore")


def download_blob(blob, file_obj, bucket):
    return bucket.blob(blob).download_to_file(file_obj)


def write_blob(key, file_obj, bucket):
    return bucket.blob(key).upload_from_file(file_obj)
