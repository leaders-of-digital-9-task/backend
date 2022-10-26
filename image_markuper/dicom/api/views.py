from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser

from ..models import Dicom
from .serializers import DicomSerializer, ListDicomSerializer


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
