import os

from utils.generators import generate_charset


def media_upload_path(instance, filename):
    return os.path.join(f"uploads/dicom/{generate_charset(7)}/", filename)
