from django.db import models
from polymorphic.models import PolymorphicModel


class BaseShape(PolymorphicModel):
    TYPE = "no_type"
    min_coordinates = None
    max_coordinates = None
    layer_fk = models.ForeignKey(
        "dicom.Layer", related_name="shapes", on_delete=models.CASCADE
    )

    def serialize_self(self):
        return {
            "id": self.id,
            "type": self.TYPE,
            "coordinates": self.coordinates,
            "layer": self.layer,
        }

    def serialize_self_without_layer(self):
        return {
            "id": self.id,
            "type": self.TYPE,
            "coordinates": self.coordinates,
        }

    @property
    def layer(self):
        return self.layer_fk.slug

    @property
    def coordinates(self) -> [(int, int)]:
        return self.shape_coordinates.all().values("x", "y")

    def __str__(self):
        return f"{self.TYPE} on {self.layer}"


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


class Roi(BaseShape):
    TYPE = "roi"


class FreeHand(BaseShape):
    TYPE = "free_hand"


class Ruler(BaseShape):
    TYPE = "ruler"
    max_coordinates = 2
    min_coordinates = 2
