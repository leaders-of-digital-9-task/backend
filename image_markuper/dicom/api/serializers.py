from dicom.models import (
    BaseShape,
    Circle,
    Coordinate,
    Dicom,
    FreeHand,
    Project,
    Roi,
    Ruler,
)
from dicom.services import create_coordinate
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.generics import get_object_or_404


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
    model = BaseShape

    type = serializers.ChoiceField(choices=["circle", "roi", "free_hand"])
    image_number = serializers.IntegerField()
    coordinates = CoordinateSerializer(many=True)

    def create(self, validated_data):
        if self.model.max_coordinates:
            if len(validated_data["coordinates"]) > self.model.max_coordinates:
                raise serializers.ValidationError
        if self.model.min_coordinates:
            if len(validated_data["coordinates"]) < self.model.min_coordinates:
                raise serializers.ValidationError
        dicom = get_object_or_404(
            Dicom, slug=self.context["request"].parser_context["kwargs"]["slug"]
        )
        obj = self.model.objects.create(
            dicom=dicom, image_number=validated_data["image_number"]
        )

        create_coordinate(validated_data["coordinates"], obj)
        return obj

    def update(self, obj, validated_data):
        Coordinate.objects.filter(shape=obj).delete()
        if self.model.max_coordinates:
            if len(validated_data["coordinates"]) > self.model.max_coordinates:
                raise serializers.ValidationError
        if self.model.min_coordinates:
            if len(validated_data["coordinates"]) < self.model.min_coordinates:
                raise serializers.ValidationError
        create_coordinate(validated_data["coordinates"], obj)
        return obj


class BaseShapeLayerSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["circle", "roi", "free_hand"])
    radius = serializers.FloatField(required=False)
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


class RoiSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    model = Roi

    class Meta:
        model = Roi
        fields = ["id", "image_number", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


class FreeHandSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    model = FreeHand

    class Meta:
        model = FreeHand
        fields = ["id", "image_number", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


class RulerSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    model = Ruler

    class Meta:
        model = FreeHand
        fields = ["id", "image_number", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


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


class ListProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="get_update_delete_project", lookup_field="slug"
    )

    class Meta:
        model = Project
        fields = ["slug", "url", "created"]
        extra_kwargs = {
            "slug": {"read_only": True},
            "created": {"read_only": True},
        }

    def create(self, validated_data):
        return Project.objects.create(user=self.context["request"].user)


class ProjectSerializer(serializers.ModelSerializer):
    files = ListDicomSerializer(many=True)

    class Meta:
        model = Project
        fields = ["files", "slug", "created"]


class PatologyGenerateSerializer(serializers.Serializer):
    project_slug = serializers.CharField()
    points = serializers.ListField(child=CoordinateSerializer())
    depth = serializers.ListField(child=serializers.IntegerField())
