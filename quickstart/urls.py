from django.urls import path, include
from rest_framework import routers

from django.conf import settings
from django.conf.urls.static import static

from quickstart.views import (
    UserViewSet, GroupViewSet,
    CarreraViewSet, MateriaViewSet,
    AlumnoViewSet, InscripcionViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'carreras', CarreraViewSet)
router.register(r'materias', MateriaViewSet)
router.register(r'alumnos', AlumnoViewSet)
router.register(r'inscripciones', InscripcionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
