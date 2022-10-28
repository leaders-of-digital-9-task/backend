from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser

from ..models import Circle, Dicom, Polygon
from .serializers import (
    CircleSerializer,
    DicomSerializer,
    ListDicomSerializer,
    PolygonSerializer,
)


class ListCreateDicomApi(generics.ListCreateAPIView):
    serializer_class = ListDicomSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Dicom.objects.filter(user=self.request.user)

    @extend_schema(
        operation_id="upload_file",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateDeleteDicomApi(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Dicom.objects.filter(user=self.request.user)

    serializer_class = DicomSerializer
    parser_classes = [MultiPartParser, FormParser]

    lookup_field = "slug"


class CreatePolygonApi(generics.CreateAPIView):
    serializer_class = PolygonSerializer


class CreateCircleApi(generics.CreateAPIView):
    serializer_class = CircleSerializer


class RetrieveUpdateDeletePolygonApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PolygonSerializer

    def get_object(self):
        return get_object_or_404(
            Polygon, id=self.request.parser_context["kwargs"]["id"]
        )

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
