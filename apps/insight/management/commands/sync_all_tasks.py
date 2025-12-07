from celery.result import AsyncResult
from django.core.management.base import BaseCommand
from tqdm import tqdm

from vidra_kit.celery_app import get_celery_app
from ...models import Task


class Command(BaseCommand):
    help = "Sync all tasks from Celery backend into Django database"

    def handle(self, *args, **kwargs):
        app = get_celery_app("production")
        # If you have a list of task IDs stored somewhere, e.g., in Flower DB or Redis:

        tasks = Task.objects.all()
        for task in tqdm(tasks, desc="Syncing tasks", unit="task"):
            self.sync_task(task, app)

        self.stdout.write(self.style.SUCCESS("All tasks synced successfully."))

    def sync_task(self, task, app):
        """
        Load task from AsyncResult and save/update Task & TaskResult models.
        """
        result = AsyncResult(task.id, app=app)

        try:
            task.result = str(result.result)
            task.save()
        except Exception as exc:
            self.stderr.write(f"Error syncing task {task.id}: {exc}")
        # assert False
        # --- TaskResult ---
