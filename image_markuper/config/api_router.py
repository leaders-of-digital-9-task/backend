from dicom.api.views import (
    AddDicomProjectApi,
    CreateCircleApi,
    CreateFreeHandApi,
    CreateRoiApi,
    CreateRulerApi,
    DeleteDicomProjectApi,
    GeneratePatology,
    ListCreateDicomApi,
    ListCreateProjectApi,
    ListUpdateDicomImageNumberApi,
    RetrieveUpdateDeleteCircleApi,
    RetrieveUpdateDeleteDicomApi,
    RetrieveUpdateDeleteFreeHandApi,
    RetrieveUpdateDeleteProjectApi,
    RetrieveUpdateDeleteRoiApi,
    RetrieveUpdateDeleteRulerApi,
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
                path("", ListCreateDicomApi.as_view(), name="dicom_list_create"),
                path("upload", SmartFileUploadApi.as_view(), name="upload_dicom_api"),
                path(
                    "<str:slug>",
                    RetrieveUpdateDeleteDicomApi.as_view(),
                    name="get_update_delete_dicom",
                ),
                path(
                    "<str:slug>/roi",
                    CreateRoiApi.as_view(),
                    name="create_roi",
                ),
                path(
                    "<str:slug>/free_hand",
                    CreateFreeHandApi.as_view(),
                    name="create_free_hand",
                ),
                path(
                    "<str:slug>/circle",
                    CreateCircleApi.as_view(),
                    name="create_circle",
                ),
                path(
                    "<str:slug>/ruler",
                    CreateRulerApi.as_view(),
                    name="create_ruler",
                ),
                path(
                    "<str:slug>/<int:layer>",
                    ListUpdateDicomImageNumberApi.as_view(),
                    name="update_dicom_layer",
                ),
            ]
        ),
    ),
    path(
        "shapes/",
        include(
            [
                path(
                    "roi/<int:id>",
                    RetrieveUpdateDeleteRoiApi.as_view(),
                    name="get_update_delete_roi",
                ),
                path(
                    "free_hand/<int:id>",
                    RetrieveUpdateDeleteFreeHandApi.as_view(),
                    name="get_update_delete_free_hand",
                ),
                path(
                    "circle/<int:id>",
                    RetrieveUpdateDeleteCircleApi.as_view(),
                    name="get_update_delete_circle",
                ),
                path(
                    "ruler/<int:id>",
                    RetrieveUpdateDeleteRulerApi.as_view(),
                    name="get_update_delete_ruler",
                ),
            ]
        ),
    ),
    path(
        "project/",
        include(
            [
                path("", ListCreateProjectApi.as_view(), name="list_create_project"),
                path(
                    "<str:slug>",
                    RetrieveUpdateDeleteProjectApi.as_view(),
                    name="get_update_delete_project",
                ),
                path(
                    "<str:slug>/upload",
                    AddDicomProjectApi.as_view(),
                    name="add_dicom_api",
                ),
                path(
                    "<str:slug>/<str:dicom_slug>",
                    DeleteDicomProjectApi.as_view(),
                    name="delete_dicom_api",
                ),
            ]
        ),
    ),
    path(
        "generate/",
        include(
            [
                path("patology", GeneratePatology.as_view(), name="generate_patology"),
            ]
        ),
    ),
]
