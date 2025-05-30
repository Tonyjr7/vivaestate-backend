from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet

router = DefaultRouter()
router.register(r"leads", LeadViewSet, basename="leads")

urlpatterns = [
    path("", include(router.urls)),
]
