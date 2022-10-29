from dicom.api.views import (
    CreateCircleApi,
    CreatePolygonApi,
    ListCreateDicomApi,
    RetrieveUpdateDeleteCircleApi,
    RetrieveUpdateDeleteDicomApi,
    RetrieveUpdateDeletePolygonApi,
    SmartFileUploadApi,
)
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.api.views import RegisterView

urlpatterns = [
    path(
        "auth/",
        include(
            [
                path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
                path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
                path("register/", RegisterView.as_view(), name="user_register"),
            ]
        ),
    ),
    path(
        "dicom/",
        include(
            [
                path("", ListCreateDicomApi.as_view(), name="list_create_dicom"),
                path("upload", SmartFileUploadApi.as_view(), name="upload_dicom_api"),
                path(
                    "<str:slug>",
                    RetrieveUpdateDeleteDicomApi.as_view(),
                    name="get_update_delete_dicom",
                ),
                path(
                    "<str:slug>/polygon",
                    CreatePolygonApi.as_view(),
                    name="create_polygon",
                ),
                path(
                    "<str:slug>/circle",
                    CreateCircleApi.as_view(),
                    name="create_circle",
                ),
            ]
        ),
    ),
    path(
        "shapes/",
        include(
            [
                path(
                    "polygon/<int:id>",
                    RetrieveUpdateDeletePolygonApi.as_view(),
                    name="get_update_delete_polygon",
                ),
                path(
                    "circle/<int:id>",
                    RetrieveUpdateDeleteCircleApi.as_view(),
                    name="get_update_delete_circle",
                ),
            ]
        ),
    ),
]
