from dicom.models import Dicom
from django.db.models.signals import pre_save
from django.dispatch import receiver
from utils.generators import generate_charset


@receiver(pre_save, sender=Dicom)
def create_dicom(sender, instance: Dicom, **kwargs):
    slug = generate_charset(5)
    while Dicom.objects.filter(slug=slug):
        slug = generate_charset(5)
    instance.slug = slug
