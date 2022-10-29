from dicom.models import Circle, Coordinate, Dicom, Roi
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.generics import get_object_or_404


def create_coordinate(coordinates, obj):
    for coordinate in coordinates:
        Coordinate.objects.create(
            x=coordinate["x"],
            y=coordinate["y"],
            shape=obj,
        )


class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = ["x", "y"]


class ListDicomSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="get_update_delete_dicom", lookup_field="slug"
    )
    file = serializers.FileField()

    class Meta:
        model = Dicom
        fields = ["file", "uploaded", "pathology_type", "url"]

    def create(self, validated_data):
        return Dicom.objects.create(**validated_data, user=self.context["request"].user)


class BaseShapeSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["circle", "Roi"])
    image_number = serializers.IntegerField()
    coordinates = CoordinateSerializer(many=True)


class DicomSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    shapes = serializers.SerializerMethodField("get_dicom_shapes")

    @extend_schema_field(field=BaseShapeSerializer)
    def get_dicom_shapes(self, obj):
        return [x.serialize_self() for x in obj.shapes.all()]

    class Meta:
        model = Dicom
        fields = ["file", "uploaded", "pathology_type", "shapes"]


class RoiSerializer(serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)

    class Meta:
        model = Roi
        fields = ["id", "image_number", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}

    def create(self, validated_data):
        if "coordinates" not in validated_data:
            raise serializers.ValidationError
        dicom = get_object_or_404(
            Dicom, slug=self.context["request"].parser_context["kwargs"]["slug"]
        )
        roi = Roi.objects.create(
            dicom=dicom, image_number=validated_data["image_number"]
        )

        create_coordinate(validated_data["coordinates"], roi)
        return roi

    def update(self, obj: Circle, validated_data):
        Coordinate.objects.filter(shape=obj).delete()
        create_coordinate(validated_data["coordinates"], obj)
        return obj


class CircleSerializer(serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)

    class Meta:
        model = Circle
        fields = ["id", "image_number", "radius", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}

    def create(self, validated_data):
        if (
            "coordinates" not in validated_data
            and len(validated_data["coordinates"]) > 1
        ):
            raise serializers.ValidationError
        dicom = get_object_or_404(
            Dicom, slug=self.context["request"].parser_context["kwargs"]["slug"]
        )
        circle = Circle.objects.create(
            dicom=dicom,
            image_number=validated_data["image_number"],
            radius=validated_data["radius"],
        )

        create_coordinate(validated_data["coordinates"], circle)
        return circle

    def update(self, obj: Circle, validated_data):
        Coordinate.objects.filter(shape=obj).delete()
        create_coordinate(validated_data["coordinates"], obj)
        if "radius" in validated_data:
            obj.radius = validated_data["radius"]
            obj.save()
        return obj


class SmartFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
