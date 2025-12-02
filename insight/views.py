from celery.result import AsyncResult
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from vidra_kit.celery_app.celery_manager import CeleryManager
from .models import Task
from .serializers import TaskSerializer, TaskResultSerializer

# Import the Celery application instance
# This assumes 'celery_config.py' is accessible or properly configured in your environment.
try:
    # from celery_config import app
    from backend.celery import app
except ImportError:
    # Handle case where celery_config is not found during import
    raise ImproperlyConfigured("Could not import 'app' from celery_config. Make sure the file is in the project root.")

class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides list and retrieve endpoints for Tasks.
    """
    queryset = Task.objects.all().order_by("-sent_at")
    serializer_class = TaskSerializer

    # Example: GET /api/tasks/{id}/result/
    @action(detail=True, methods=["get"])
    def result(self, request, pk=None):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch result from Celery
        celery_app = get_celery_app()  # replace with async if you use async Celery app
        result = AsyncResult(task.id, app=celery_app)

        task_result_data = {
            "id": result.id,
            "type": result.name,
            "state": result.state,
            "queue": getattr(result, "queue", None),
            "result": result.result,
            "traceback": str(result.traceback) if result.traceback else None,
            "ignored": getattr(result, "ignored", False),
            "args": result.args or [],
            "kwargs": result.kwargs or {},
            "retries": result.retries or 0,
            "worker": getattr(result, "worker", None),
        }

        serializer = TaskResultSerializer(task_result_data)
        return Response(serializer.data)

class TaskViewSet2(ViewSet):

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        """
        Start a long running task.
        Optional POST body: {"seconds": 15}
        """
        seconds = int(request.data.get("seconds", 10))
        task = long_task.delay(seconds)

        return Response(
            {"task_id": task.id, "message": "Task started"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["get"], url_path="status")
    def status(self, request):
        """
        Check task status: /tasks/status/?id=<task_id>
        """
        task_id = request.query_params.get("id")
        if not task_id:
            return Response({"error": "Missing ?id="}, status=400)

        result = AsyncResult(task_id)

        return Response(
            {
                "task_id": task_id,
                "state": result.state,
                "ready": result.ready(),
                "result": result.result if result.ready() else None,
            }
        )


def get_celery_stats_sync():
    """
    Synchronous function to interact with Celery's inspection API.
    This function blocks and should be called from an executor or separate thread.
    """
    i = app.control.inspect()

    # 1. Active workers
    active_workers = i.ping()

    # 2. Currently running tasks
    active_tasks = i.active()

    # 3. Scheduled (delayed) tasks
    scheduled_tasks = i.scheduled()

    # 4. Registered tasks (list of all available task functions)
    registered_tasks = i.registered()

    stats = {
        "workers_online": len(active_workers) if active_workers else 0,
        "workers": active_workers,
        "active_tasks_count": sum(len(tasks) for tasks in active_tasks.values()) if active_tasks else 0,
        "active_tasks": active_tasks,
        "scheduled_tasks": scheduled_tasks,
        "registered_tasks": registered_tasks,
    }
    return stats

# CeleryManager

class CeleryViewSet(ViewSet):
    """
    A DRF ViewSet providing an async endpoint to fetch Celery worker stats.
    """

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        try:
            stats = get_celery_stats_sync()
            print(
                f"Celery stats: {stats}"
            )
            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            # Log in real app
            print(f"Error fetching Celery stats: {e}")
            return Response(
                {"error": "Failed to connect to or inspect Celery workers."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)


class QueueViewSet(ViewSet):

    @action(detail=False, methods=["get"], url_path="items")
    def items(self, request):
        queue = request.query_params.get("queue", "celery")
        items = r.lrange(queue, 0, -1)

        decoded = []
        for raw in items:
            try:
                decoded.append(json.loads(raw))
            except:
                decoded.append(raw.decode())

        return Response({"queue": queue, "count": len(decoded), "items": decoded})
