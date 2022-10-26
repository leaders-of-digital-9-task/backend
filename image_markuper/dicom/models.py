from django.contrib.auth import get_user_model
from django.db import models
from utils.files import media_upload_path

User = get_user_model()


class Dicom(models.Model):
    user = models.ForeignKey(User, related_name="files", on_delete=models.CASCADE)
    slug = models.SlugField()

    file = models.FileField(upload_to=media_upload_path)
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
