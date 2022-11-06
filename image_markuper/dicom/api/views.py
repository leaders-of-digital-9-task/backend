from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from ..models import Circle, Dicom, FreeHand, Layer, Project, Roi, Ruler
from ..services import process_files
from .serializers import (
    BaseShapeLayerSerializer,
    BaseShapeSerializer,
    CircleSerializer,
    DicomSerializer,
    FreeHandSerializer,
    LayerSerializer,
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
        return Dicom.objects.all()


class RetrieveUpdateDeleteDicomApi(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Dicom.objects.all()

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
        responses={200: DicomSerializer},
        operation_id="get_dicom_layer",
    )
    def get(self, request, dicom_slug):
        return Response(
            DicomSerializer(
                get_object_or_404(Dicom, slug=dicom_slug), context={"request": request}
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=BaseShapeLayerSerializer(many=True),
        responses={201: DicomSerializer},
        operation_id="update_dicom_layer",
    )
    def put(self, request, dicom_slug):
        dicom = get_object_or_404(Dicom, slug=dicom_slug)
        dicom.delete_shapes()
        serializer = BaseShapeLayerSerializer(
            data=request.data, many=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        for shape in serializer.data:
            layer = Layer.objects.get(slug=shape["layer"])
            if shape["type"] == "circle":
                obj = Circle.objects.create(layer_fk=layer, radius=shape["radius"])
            elif shape["type"] == "roi":
                obj = Roi.objects.create(layer_fk=layer)
            elif shape["type"] == "free_hand":
                obj = FreeHand.objects.create(layer_fk=layer)
            else:
                obj = Ruler.objects.create(layer_fk=layer)
            create_coordinate(shape["coordinates"], obj)
        return Response(
            DicomSerializer(dicom, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={204: None},
        operation_id="delete_dicom_layer",
    )
    def delete(self, request, dicom_slug):
        dicom = get_object_or_404(Dicom, slug=dicom_slug)
        dicom.shapes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateProjectApi(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.user.is_staff:
            s = ListProjectSerializer
            s.Meta.fields.append("user_username")
            return s
        return ListProjectSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(user=self.request.user)

    @extend_schema(
        description="""(0, 'Без патологий'),
 (1, 'COVID-19; все доли; многочисленные; размер любой'),
 (2, 'COVID-19; Нижняя доля правого лёгкого, Нижняя доля левого лёгкого'),
 (3, 'Немногочисленные; 10-20 мм'),
 (4, 'Рак лёгкого; Нижняя доля правого лёгкого, Единичное; 10-20 мм'),
 (5, 'Рак лёгкого; Средняя доля правого лёгкого, Единичное; >20 мм'),
 (6, 'Рак лёгкого; Нижняя доля левого лёгкого, Единичное; 10-20 мм'),
 (7, 'Рак лёгкого; Верхняя доля правого лёгкого, Единичное; 5-10 мм'),
 (8, 'Рак лёгкого; Верхняя доля левого лёгкого, Единичное; 5-10 мм'),
 (9, 'Метастатическое поражение лёгких; Все доли; Многочисленные; 5-10 мм'),
 (10, 'Метастатическое поражение лёгких; Все доли; Многочисленные; 10-20 мм'),
 (11, 'Метастатическое поражение лёгких; Все доли; Немногочисленные; 5-10 мм')"""
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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


class CreateLayerApi(generics.CreateAPIView):
    serializer_class = LayerSerializer


class RetrieveUpdateDeleteLayerApi(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LayerSerializer
    queryset = Layer.objects.all()

    lookup_field = "slug"
