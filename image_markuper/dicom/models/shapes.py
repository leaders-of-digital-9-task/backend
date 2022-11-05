from dicom.models import Layer
from django.db import models
from polymorphic.models import PolymorphicModel


class BaseShape(PolymorphicModel):
    TYPE = "no_type"
    min_coordinates = None
    max_coordinates = None
    layer = models.ForeignKey(Layer, related_name="shapes", on_delete=models.CASCADE)

    def serialize_self(self):
        return {
            "id": self.id,
            "type": self.TYPE,
            "image_number": self.image_number,
            "coordinates": self.coordinates,
        }

    def serialize_self_without_layer(self):
        return {
            "id": self.id,
            "type": self.TYPE,
            "coordinates": self.coordinates,
        }

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
    radius = models.FloatField()
    max_coordinates = 1

    def serialize_self(self):
        return {
            "id": self.id,
            "type": "circle",
            "image_number": self.image_number,
            "radius": self.radius,
            "coordinates": self.coordinates,
        }

    def serialize_self_without_layer(self):
        return {
            "id": self.id,
            "type": "circle",
            "radius": self.radius,
            "coordinates": self.coordinates,
        }

    def __str__(self):
        return f"circle on {self.dicom.file.name}"


class Roi(BaseShape):
    TYPE = "roi"

    def __str__(self):
        return f"Roi on {self.dicom.file.name}"


class FreeHand(BaseShape):
    TYPE = "free_hand"

    def __str__(self):
        return f"FreeHand on {self.dicom.file.name}"


class Ruler(BaseShape):
    TYPE = "ruler"
    max_coordinates = 2
    min_coordinates = 2

    def __str__(self):
        return f"Ruler on {self.dicom.file.name}"
