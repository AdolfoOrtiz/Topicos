from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers
from quickstart.views import (
    CustomAuthToken, RegisterAPIView, MeAPIView,
    ResetTokenAPIView, LogoutAPIView
)


from quickstart import views


router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("", include("quickstart.urls")),
    path("api/", include("quickstart.urls")), 
    path("api-auth/", include("rest_framework.urls", 
    namespace="rest_framework")),
    re_path(r"^api/custom-token/?$", CustomAuthToken.as_view(), name='custom_auth_token'),
    re_path(r"^custom-token/?$", CustomAuthToken.as_view(), name='custom_auth_token_root'),
    re_path(r"^api/register/?$", RegisterAPIView.as_view(), name='register'),
    re_path(r"^register/?$", RegisterAPIView.as_view(), name='register_root'),
    re_path(r"^api/me/?$", MeAPIView.as_view(), name="me"),
    re_path(r"^me/?$", MeAPIView.as_view(), name="me_root"),
    re_path(r"^api/resettoken/?$", ResetTokenAPIView.as_view(), name='reset_token'),
    re_path(r"^resettoken/?$", ResetTokenAPIView.as_view(), name='reset_token_root'),
    re_path(r"^api/reset-token/?$", ResetTokenAPIView.as_view(), name='reset_token_hyphen'),
    re_path(r"^reset-token/?$", ResetTokenAPIView.as_view(), name='reset_token_hyphen_root'),
    re_path(r"^api/logout/?$", LogoutAPIView.as_view(), name='logout'),
    re_path(r"^logout/?$", LogoutAPIView.as_view(), name='logout_root'),
]

