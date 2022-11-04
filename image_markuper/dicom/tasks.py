from celery import shared_task
from dicom import services
from dicom.models import Project


@shared_task()
def process_project(pk: int):
    services.generate_3d_model(Project.objects.get(pk=pk))
    return pk
