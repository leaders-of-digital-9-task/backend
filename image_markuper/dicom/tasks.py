from celery import shared_task
from dicom.models import Project
from dicom.services import generate_3d_model


@shared_task()
def process_project(slug: str):
    print(slug)
    generate_3d_model(Project.objects.get(slug=slug))
    return slug
