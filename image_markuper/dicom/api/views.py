from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from ..models import Circle, Dicom, Roi
from ..services import process_files
from .serializers import (
    BaseShapeLayerSerializer,
    BaseShapeSerializer,
    CircleSerializer,
    DicomSerializer,
    ListDicomSerializer,
    RoiSerializer,
    SmartFileUploadSerializer,
    create_coordinate,
)


class ListCreateDicomApi(generics.ListCreateAPIView):
    serializer_class = ListDicomSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Dicom.objects.filter(user=self.request.user)


class RetrieveUpdateDeleteDicomApi(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Dicom.objects.filter(user=self.request.user)

    serializer_class = DicomSerializer
    parser_classes = [MultiPartParser, FormParser]

    lookup_field = "slug"


class CreateRoiApi(generics.CreateAPIView):
    serializer_class = RoiSerializer


class CreateCircleApi(generics.CreateAPIView):
    serializer_class = CircleSerializer


class RetrieveUpdateDeleteRoiApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoiSerializer

    def get_object(self):
        return get_object_or_404(Roi, id=self.request.parser_context["kwargs"]["id"])

    @extend_schema(description="Note: coordinated are dropped on update")
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(description="Note: coordinated are dropped on update")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveUpdateDeleteCircleApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CircleSerializer

    def get_object(self):
        return get_object_or_404(Circle, id=self.request.parser_context["kwargs"]["id"])

    @extend_schema(description="Note: coordinated are dropped on update")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(description="Note: coordinated are dropped on update")
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class SmartFileUploadApi(GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = SmartFileUploadSerializer

    @extend_schema(responses={201: DicomSerializer(many=True)})
    def post(self, request):
        if "file" not in request.data:
            raise ValidationError("no files")
        d_list = process_files(request.FILES.getlist("file"), request.user)
        return Response(
            DicomSerializer(d_list.files.all(), many=True).data,
            status=status.HTTP_201_CREATED,
        )


class ListUpdateDicomImageNumberApi(GenericAPIView):
    serializer_class = BaseShapeSerializer(many=True)

    @extend_schema(
        request=None,
        responses={200: BaseShapeSerializer(many=True)},
        operation_id="get_dicom_layer",
    )
    def get(self, request, slug, layer):
        shapes = [
            x.serialize_self_without_layer()
            for x in get_object_or_404(Dicom, slug=slug).shapes.filter(
                image_number=layer
            )
        ]
        return Response(shapes, status=status.HTTP_200_OK)

    @extend_schema(
        request=BaseShapeLayerSerializer(many=True),
        responses={201: DicomSerializer},
        operation_id="update_dicom_layer",
    )
    def put(self, request, slug, layer):
        dicom = get_object_or_404(Dicom, slug=slug)
        dicom.shapes.filter(image_number=layer).delete()
        serializer = BaseShapeLayerSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        for shape in serializer.data:
            if shape["type"] == "circle":
                obj = Circle.objects.create(
                    dicom=dicom, image_number=layer, radius=shape["radius"]
                )
                if len(shape["coordinates"]) > 1:
                    raise ValidationError
            elif shape["type"] == "roi":
                obj = Roi.objects.create(dicom=dicom, image_number=layer)
            create_coordinate(shape["coordinates"], obj)
        shapes = [
            x.serialize_self_without_layer()
            for x in get_object_or_404(Dicom, slug=slug).shapes.filter(
                image_number=layer
            )
        ]
        return Response(shapes, status=status.HTTP_200_OK)
