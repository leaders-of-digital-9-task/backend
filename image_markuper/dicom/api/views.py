from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Circle, Dicom, Polygon
from ..services import process_files
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


class SmartFileUploadApi(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if "file" not in request.data:
            raise ValidationError("no files")
        d_list = process_files(request.FILES.getlist("file"), request.user)
        return Response(
            DicomSerializer(d_list.files.all(), many=True).data,
            status=status.HTTP_201_CREATED,
        )
