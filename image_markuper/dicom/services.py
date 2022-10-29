import glob
import os
import shutil
import zipfile
from pathlib import Path

import magic
from dicom.models import Dicom, ListOfDicom
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from utils.generators import generate_charset


def process_files(files: list[TemporaryUploadedFile | InMemoryUploadedFile], user):
    d_list = ListOfDicom.objects.create()
    for file in files:
        content_type = magic.from_file(file.temporary_file_path())
        if content_type == "DICOM medical imaging data":
            Dicom.objects.create(file=file, list=d_list, user=user)
        elif "Zip" in content_type:
            dit_path = f"/tmp/{generate_charset(10)}"
            os.mkdir(dit_path)
            with zipfile.ZipFile(file.temporary_file_path(), "r") as zip_ref:
                zip_ref.extractall(dit_path)
            files = glob.glob(dit_path + "/**/*", recursive=True)

            for file_in_d in files:
                if not os.path.isdir(file_in_d):
                    content_type = magic.from_file(file_in_d)
                    if content_type == "DICOM medical imaging data":
                        path = Path(file_in_d)
                        with path.open(mode="rb") as f:
                            Dicom.objects.create(
                                file=File(f, name=file_in_d.split("/")[-1]),
                                list=d_list,
                                user=user,
                            )
            shutil.rmtree(dit_path)
    return d_list
