from django.core.management.base import BaseCommand
from django.utils import timezone
from celery.result import AsyncResult, GroupResult
from celery_app import get_celery_app
from tasks.models import Task, TaskResult

class Command(BaseCommand):
    help = "Sync all tasks from Celery backend into Django database"

    def handle(self, *args, **kwargs):
        app = get_celery_app()
        # If you have a list of task IDs stored somewhere, e.g., in Flower DB or Redis:
        task_ids = self.get_all_task_ids(app)

        self.stdout.write(f"Found {len(task_ids)} tasks. Syncing...")

        for task_id in task_ids:
            self.sync_task(task_id, app)

        self.stdout.write(self.style.SUCCESS("All tasks synced successfully."))

    def get_all_task_ids(self, app):
        """
        Collect all task IDs from backend.
        - Option 1: Flower API (recommended for historical tasks)
        - Option 2: Redis backend scan (if storing task IDs)
        """
        # Example with Flower API
        import requests
        FLOWER_API_URL = "http://localhost:5555/api/tasks"
        try:
            response = requests.get(FLOWER_API_URL)
            response.raise_for_status()
            data = response.json()
            return [task["id"] for task in data]
        except Exception:
            self.stdout.write(self.style.WARNING("Flower API not available. No tasks fetched."))
            return []

    def sync_task(self, task_id, app):
        """
        Load task from AsyncResult and save/update Task & TaskResult models.
        """
        result = AsyncResult(task_id, app=app)

        # --- Task ---
        Task.objects.update_or_create(
            id=result.id,
            defaults={
                "type": result.name,
                "state": result.state,
                "worker": getattr(result, "worker", None),
                "args": str(result.args) if result.args else None,
                "kwargs": str(result.kwargs) if result.kwargs else None,
                "retries": result.retries or 0,
                "sent_at": getattr(result, "date_done", timezone.now()),
                "last_updated": timezone.now(),
                "result": str(result.result) if result.result else None,
                "traceback": str(result.traceback) if result.traceback else None,
            },
        )

        # --- TaskResult ---
        TaskResult.objects.update_or_create(
            id=result.id,
            defaults={
                "type": result.name,
                "state": result.state,
                "queue": getattr(result, "queue", None),
                "worker": getattr(result, "worker", None),
                "result": str(result.result) if result.result else None,
                "traceback": str(result.traceback) if result.traceback else None,
                "ignored": getattr(result, "ignored", False),
                "args": result.args or [],
                "kwargs": result.kwargs or {},
                "retries": result.retries or 0,
            },
        )
