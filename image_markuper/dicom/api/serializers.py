from dicom.models import (
    BaseShape,
    Circle,
    Coordinate,
    Dicom,
    FreeHand,
    Layer,
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


class ListProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="get_update_delete_project", lookup_field="slug"
    )

    class Meta:
        model = Project
        fields = ["name", "pathology_type", "slug", "url", "created"]
        extra_kwargs = {
            "slug": {"read_only": True},
            "created": {"read_only": True},
        }

    def create(self, validated_data):
        return Project.objects.create(
            user=self.context["request"].user,
            name=validated_data["name"],
            pathology_type=validated_data["pathology_type"],
        )


class ListDicomSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="get_update_delete_dicom", lookup_field="slug"
    )
    file = serializers.FileField()

    class Meta:
        model = Dicom
        fields = ["file", "uploaded", "url"]

    def create(self, validated_data):
        return Dicom.objects.create(**validated_data, user=self.context["request"].user)


class ProjectSerializer(serializers.ModelSerializer):
    files = ListDicomSerializer(many=True)

    class Meta:
        model = Project
        fields = ["files", "slug", "created", "stl"]


class BaseShapeSerializer(serializers.Serializer):
    model = BaseShape

    type = serializers.ChoiceField(choices=["circle", "roi", "free_hand", "ruler"])
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)
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
        if validated_data["layer"]:
            layer = get_object_or_404(Layer, slug=validated_data["layer"])
        else:
            layer = dicom.layers.filter(parent__isnull=True).first()

        obj = self.model.objects.create(layer_fk=layer)

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
        if validated_data["layer"]:
            layer = get_object_or_404(Layer, slug=validated_data["layer"])
        else:
            layer = obj.dicom.layers.filter(parent__isnull=True).first()
        if obj.layer_fk != layer:
            obj.layer_fk = layer
            obj.save()
        create_coordinate(validated_data["coordinates"], obj)
        return obj


class BaseShapeLayerSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["circle", "roi", "free_hand", "ruler"])
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)
    radius = serializers.FloatField(required=False)
    coordinates = CoordinateSerializer(many=True)


class LayerChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layer
        fields = ["name", "slug"]


class LayerSerializer(serializers.ModelSerializer):
    children = LayerChildSerializer(many=True, read_only=True)
    parent = serializers.SlugField(max_length=8, allow_blank=True, write_only=True)

    def validate_parent(self, val):
        if val:
            return get_object_or_404(Layer, slug=val)
        return (
            get_object_or_404(
                Dicom,
                slug=self.context["request"].parser_context["kwargs"]["dicom_slug"],
            )
            .layers.filter(parent__isnull=True)
            .first()
        )

    class Meta:
        model = Layer
        fields = ["name", "slug", "children", "parent"]
        extra_kwargs = {
            "children": {"read_only": True},
            "slug": {"read_only": True},
            "parent": {"write_only": True},
        }

    def create(self, validated_data):
        return Layer.objects.create(
            name=validated_data["name"],
            dicom=validated_data["parent"].dicom,
            parent=validated_data["parent"],
        )


class DicomSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    shapes = serializers.SerializerMethodField("get_dicom_shapes")
    layers = serializers.SerializerMethodField("get_dicom_layers")

    @extend_schema_field(field=BaseShapeSerializer(many=True))
    def get_dicom_shapes(self, obj):
        return [x.serialize_self() for x in obj.shapes.all()]

    @extend_schema_field(field=LayerSerializer(many=True))
    def get_dicom_layers(self, obj):
        return obj.get_layers()

    class Meta:
        model = Dicom
        fields = ["file", "uploaded", "shapes", "layers"]


class RoiSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)
    model = Roi

    class Meta:
        model = Roi
        fields = ["id", "layer", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


class FreeHandSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)
    coordinates = CoordinateSerializer(many=True)
    model = FreeHand

    class Meta:
        model = FreeHand
        fields = ["id", "layer", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


class RulerSerializer(BaseShapeSerializer, serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)
    model = Ruler

    class Meta:
        model = FreeHand
        fields = ["id", "layer", "coordinates"]
        extra_kwargs = {"id": {"read_only": True}}


class CircleSerializer(serializers.ModelSerializer):
    coordinates = CoordinateSerializer(many=True)
    layer = serializers.SlugField(max_length=8, required=False, allow_blank=True)

    class Meta:
        model = Circle
        fields = ["id", "layer", "radius", "coordinates"]
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
        if validated_data["layer"]:
            layer = get_object_or_404(Layer, slug=validated_data["layer"])
        else:
            layer = dicom.layers.filter(parent__isnull=True).first()
        circle = Circle.objects.create(
            layer_fk=layer,
            radius=validated_data["radius"],
        )

        create_coordinate(validated_data["coordinates"], circle)
        return circle

    def update(self, obj: Circle, validated_data):
        Coordinate.objects.filter(shape=obj).delete()
        create_coordinate(validated_data["coordinates"], obj)
        if validated_data["layer"]:
            layer = get_object_or_404(Layer, slug=validated_data["layer"])
        else:
            layer = obj.dicom.layers.filter(parent__isnull=True).first()
        if "radius" in validated_data:
            obj.radius = validated_data["radius"]
            obj.layer_fk = layer
            obj.save()
        return obj


class SmartFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class PatologyGenerateSerializer(serializers.Serializer):
    project_slug = serializers.CharField()
    points = serializers.ListField(child=CoordinateSerializer())
    depth = serializers.ListField(child=serializers.IntegerField())
