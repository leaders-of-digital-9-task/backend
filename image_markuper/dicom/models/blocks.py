from dicom.models import Dicom
from django.db import models
from polymorphic.models import PolymorphicModel


class BaseShape(PolymorphicModel):
    dicom = models.ForeignKey(Dicom, related_name="shapes", on_delete=models.CASCADE)
    image_number = models.IntegerField()

    def serialize_self(self):
        raise NotImplementedError

    @property
    def coordinates(self) -> [(int, int)]:
        return self.shape_coordinates.all().values("x", "y")

    def __str__(self):
        return self.dicom.file.name


class Coordinate(models.Model):
    x = models.FloatField()
    y = models.FloatField()

    shape = models.ForeignKey(
        to=BaseShape,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="shape_coordinates",
    )


class Circle(BaseShape):
    radius = models.IntegerField()

    def serialize_self(self):
        return {
            "id": self.id,
            "type": "circle",
            "image_number": self.image_number,
            "radius": self.radius,
            "coordinates": self.coordinates,
        }

    def __str__(self):
        return f"circle on {self.dicom.file.name}"


class Polygon(BaseShape):
    def serialize_self(self):
        return {
            "id": self.id,
            "type": "polygon",
            "image_number": self.image_number,
            "coordinates": self.coordinates,
        }

    def __str__(self):
        return f"polygon on {self.dicom.file.name}"
