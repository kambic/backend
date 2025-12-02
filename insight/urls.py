from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet,  CeleryViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(f"celery", CeleryViewSet, basename="celery")

urlpatterns = [

    path("api/", include(router.urls)),
]

# --- Monitor App URLs ---
