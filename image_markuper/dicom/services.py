import glob
import os
import shutil
import zipfile
from pathlib import Path

import magic
import numpy as np
import pydicom
from dicom.models import Coordinate, Dicom, Project
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from skimage import measure
from stl import mesh
from utils.generators import generate_charset


def process_files(
    files: list[TemporaryUploadedFile | InMemoryUploadedFile], user, slug=None
):
    if slug:
        project = Project.objects.get(slug=slug)
    else:
        project = Project.objects.create(user=user)
    for file in files:
        content_type = magic.from_file(file.temporary_file_path())
        if content_type == "DICOM medical imaging data":
            Dicom.objects.create(file=file, project=project, user=user)
        elif "Zip" in content_type:
            dit_path = f"tmp/{generate_charset(10)}"
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
                                project=project,
                                user=user,
                            )
            shutil.rmtree(dit_path)
    return project


def create_coordinate(coordinates, obj):
    for coordinate in coordinates:
        Coordinate.objects.create(
            x=coordinate["x"],
            y=coordinate["y"],
            shape=obj,
        )


def get_bbox(project_id, points, image_range):
    project: Project = Project.objects.get(slug=project_id)
    # print(Dicom.objects.all())
    files = project.files.all()
    bbox_data = []
    for file_number in range(image_range[0], image_range[1] + 1):
        print(points[0]["x"])
        bbox_data.append(
            pydicom.dcmread(files[file_number].file.path)
            .pixel_array[
                int(points[0]["x"]) : int(points[1]["x"]),  # noqa
                int(points[0]["y"]) : int(points[1]["y"]),  # noqa
            ]
            .tolist()
        )
        print(pydicom.dcmread(files[file_number].file.path).pixel_array)
    print(bbox_data)
    # print(project.files.all(), "files", project)
    return []


def generate_3d_point_cloud(project_slug: str):
    project = Project.objects.get(slug=project_slug)

    point_clouds = []

    for file_index, file in enumerate(project.files.all()[::10]):
        print(file_index)
        pixel_array = pydicom.dcmread(file.file.path).pixel_array
        for iindex, i in enumerate(pixel_array[::10]):
            for jindex, j in enumerate(i[::10]):
                if j <= 240:
                    pass
                    # point_clouds.append({'x': jindex, 'y': iindex, 'z': fileindex, 'value': 0})
                else:
                    point_clouds.append([jindex, iindex, file_index, j])
    return point_clouds


def generate_3d_model(project: Project, thr=800) -> str:
    image = []
    for file in project.files.all():
        image.append(pydicom.dcmread(file.file.path).pixel_array)

    p = np.array(image).transpose(2, 1, 0)
    verts, faces, normals, values = measure.marching_cubes(p, thr, step_size=1)

    solid = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            solid.vectors[i][j] = verts[f[j], :]

    pth = f"/tmp/{generate_charset(4)}.stl"
    solid.save(pth)
    return pth
