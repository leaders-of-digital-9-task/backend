from celery import shared_task
from dicom.models import Project
from dicom.services import generate_3d_model


@shared_task()
def process_dicom(pk: int):
    generate_3d_model(Project.objects.get(pk=pk))
    return pk
