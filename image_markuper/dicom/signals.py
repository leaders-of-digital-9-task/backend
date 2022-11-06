from dicom.models import Dicom, Layer, Project
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.generators import generate_charset


@receiver(post_save, sender=Project)
def create_project(sender, instance: Project, created, **kwargs):
    if created:
        slug = generate_charset(5)
        while Project.objects.filter(slug=slug):
            slug = generate_charset(5)
        instance.slug = slug
        instance.save()


@receiver(post_save, sender=Dicom)
def create_dicom(sender, instance: Dicom, created, **kwargs):
    if created:
        slug = generate_charset(5)
        while Dicom.objects.filter(slug=slug):
            slug = generate_charset(5)
        instance.slug = slug
        instance.save()
        Layer.objects.create(parent=None, dicom=instance, name="root")


@receiver(post_save, sender=Layer)
def create_layer(sender, instance: Layer, created, **kwargs):
    if created:
        slug = generate_charset(8)
        while Layer.objects.filter(slug=slug):
            slug = generate_charset(8)
        instance.slug = slug
        instance.save()
