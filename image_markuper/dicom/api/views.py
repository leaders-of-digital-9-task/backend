from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from ..models import Circle, Dicom, Project, Roi
from ..services import process_files
from .serializers import (
    BaseShapeLayerSerializer,
    BaseShapeSerializer,
    CircleSerializer,
    DicomSerializer,
    FreeHandSerializer,
    ListDicomSerializer,
    ListProjectSerializer,
    PatologyGenerateSerializer,
    ProjectSerializer,
    RoiSerializer,
    RulerSerializer,
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


class CreateFreeHandApi(generics.CreateAPIView):
    serializer_class = FreeHandSerializer


class CreateCircleApi(generics.CreateAPIView):
    serializer_class = CircleSerializer


class CreateRulerApi(generics.CreateAPIView):
    serializer_class = RulerSerializer


class RetrieveUpdateDeleteBaseShape(generics.RetrieveUpdateDestroyAPIView):
    def get_object(self):
        return get_object_or_404(
            self.serializer_class.Meta.model,
            id=self.request.parser_context["kwargs"]["id"],
        )

    @extend_schema(description="Note: coordinated are dropped on update")
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(description="Note: coordinated are dropped on update")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveUpdateDeleteRoiApi(RetrieveUpdateDeleteBaseShape):
    serializer_class = RoiSerializer


class RetrieveUpdateDeleteFreeHandApi(RetrieveUpdateDeleteBaseShape):
    serializer_class = FreeHandSerializer


class RetrieveUpdateDeleteCircleApi(RetrieveUpdateDeleteBaseShape):
    serializer_class = CircleSerializer


class RetrieveUpdateDeleteRulerApi(RetrieveUpdateDeleteBaseShape):
    serializer_class = CircleSerializer


class SmartFileUploadApi(GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = SmartFileUploadSerializer

    @extend_schema(responses={201: ListDicomSerializer(many=True)})
    def post(self, request):
        if "file" not in request.data:
            raise ValidationError("no files")
        project = process_files(
            request.FILES.getlist("file"),
            request.user,
        )
        return Response(
            ProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AddDicomProjectApi(GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = SmartFileUploadSerializer

    @extend_schema(
        operation_id="add_dicom_to_project",
        responses={201: ListDicomSerializer(many=True)},
    )
    def post(self, request, slug):
        if "file" not in request.data:
            raise ValidationError("no files")
        get_object_or_404(Project, slug=slug)
        project = process_files(
            request.FILES.getlist("file"),
            request.user,
            slug,
        )
        return Response(
            ProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class DeleteDicomProjectApi(GenericAPIView):
    serializer_class = SmartFileUploadSerializer

    @extend_schema(
        operation_id="delete_dicom_from_project",
        request=None,
        responses={200: ListDicomSerializer(many=True)},
    )
    def delete(self, request, slug, dicom_slug):
        project = get_object_or_404(Project, slug=slug)
        project.files.filter(slug=dicom_slug).delete()

        return Response(
            ProjectSerializer(project, context={"request": request}).data,
            status=status.HTTP_200_OK,
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

    @extend_schema(
        request=None,
        responses={204: None},
        operation_id="delete_dicom_layer",
    )
    def delete(self, request, slug, layer):
        dicom = get_object_or_404(Dicom, slug=slug)
        dicom.shapes.filter(image_number=layer).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateProjectApi(generics.ListCreateAPIView):
    serializer_class = ListProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


class RetrieveUpdateDeleteProjectApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    lookup_field = "slug"


class GeneratePatology(generics.CreateAPIView):
    serializer_class = PatologyGenerateSerializer

    def create(self, request, *args, **kwargs):
        # data = self.get_serializer(request.data).data
        # bbox = get_bbox(data["project_slug"], data["points"], data["depth"])
        return Response(data={}, status=200)
