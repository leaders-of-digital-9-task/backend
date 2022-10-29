from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from ..models import Circle, Dicom, Roi
from ..services import process_files
from .serializers import (
    CircleSerializer,
    DicomSerializer,
    ListDicomSerializer,
    RoiSerializer,
    SmartFileUploadSerializer,
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


class CreateroiApi(generics.CreateAPIView):
    serializer_class = RoiSerializer


class CreateCircleApi(generics.CreateAPIView):
    serializer_class = CircleSerializer


class RetrieveUpdateDeleteroiApi(generics.RetrieveUpdateDestroyAPIView):
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


class UpdateDicomLayerApi(GenericAPIView):
    serializer_class = SmartFileUploadSerializer
