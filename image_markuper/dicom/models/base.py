from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from utils.files import media_upload_path

User = get_user_model()


class ListOfDicom(models.Model):
    pass


class Dicom(models.Model):
    class PathologyType(models.IntegerChoices):
        no_pathology = 0, "Без патологий"
        covid_pathology = 1, "Covid"

    user = models.ForeignKey(User, related_name="files", on_delete=models.CASCADE)
    slug = models.SlugField()

    file = models.FileField(upload_to=media_upload_path)
    uploaded = models.DateTimeField(auto_now_add=True)

    pathology_type = models.IntegerField(choices=PathologyType.choices, default=0)
    list = models.ForeignKey(
        ListOfDicom, related_name="files", null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.file.name

    def get_absolute_url(self):
        return reverse("get_update_delete_dicom", kwargs={"slug": self.slug})
