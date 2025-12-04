from celery.result import AsyncResult
from django.utils import timezone
from .models import Task, TaskResult
from vidra_kit.celery_app import get_celery_app


def sync_task_from_asyncresult(task_id: str):
    """
    Load a task from Celery AsyncResult and save/update it in Django DB.
    """
    result = AsyncResult(task_id, app=app)

    # --- Task model ---
    Task.objects.update_or_create(
        id=result.id,
        defaults={
            "type": result.name,
            "state": result.state,
            "worker": getattr(result, "worker", None),
            "args": str(result.args) if result.args else None,
            "kwargs": str(result.kwargs) if result.kwargs else None,
            "retries": result.retries or 0,
            "sent_at": getattr(
                result, "date_done", timezone.now()
            ),  # optional fallback
            "last_updated": timezone.now(),
            "result": str(result.result) if result.result else None,
            "traceback": str(result.traceback) if result.traceback else None,
        },
    )

    # --- TaskResult model ---

    return result
