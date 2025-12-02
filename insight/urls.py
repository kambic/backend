from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CeleryViewSet, QueueViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(f"celery", CeleryViewSet, basename="celery")
router.register(f"q", QueueViewSet, basename="q")

urlpatterns = [

    path("api/", include(router.urls)),
]

# --- Monitor App URLs ---
