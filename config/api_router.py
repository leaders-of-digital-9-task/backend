from dicom.api.views import ListCreateDicomApi, RetrieveUpdateDeleteDicomApi
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
                path(
                    "<str:slug>",
                    RetrieveUpdateDeleteDicomApi.as_view(),
                    name="get_update_delete_dicom",
                ),
            ]
        ),
    ),
]
