import json
from datetime import datetime
from pprint import pprint

from django.core.management.base import BaseCommand
from django_celery_results.models import TaskResult

from insight.models import TaskEvent
from vidra_kit.celery_app import get_celery_app
from vidra_kit import logger
from vidra_kit.celery_app.events.receiver import CeleryEventReceiver, EventProcessor
from backend.celery import app


class DjangoEventProcessor(EventProcessor):
    def process_event(self, event: dict):
        logger.info(f"Processing event {event['type']}")

        # Example function within your custom event receiver's handler
        task_id = event["uuid"]  # Assuming 'uuid' is the task ID
        state = event["state"]

        data = {
            "task_id": task_id,
            "status": state,
            "task_name": event.get("name", "N/A"),
            "date_done": datetime.fromtimestamp(event["timestamp"]),
        }

        if state == "SUCCESS":
            # You must serialize the result value into a JSON string
            data["result"] = json.dumps(event.get("result"))
            data["meta"] = json.dumps(
                {
                    "task_args": event.get("args", []),
                    "task_kwargs": event.get("kwargs", {}),
                }
            )
        elif state == "FAILURE":
            # Store the exception and traceback
            data["result"] = json.dumps(event.get("exception", "Unknown Error"))
            data["traceback"] = event.get("traceback", "N/A")

        # Create or update the TaskResult instance
        try:
            TaskResult.objects.update_or_create(task_id=task_id, defaults=data)
            print(f"Successfully stored legacy result for task {task_id}")
        except Exception as e:
            print(f"Error storing result for {task_id}: {e}")


class Command(BaseCommand):
    help = "Subscribe to Celery events"

    def handle(self, *args, **options):
        logger.info(f"Starting Celery event receiver for app {app.conf.broker_url}")
        receiver = CeleryEventReceiver(app, processor=DjangoEventProcessor)
        receiver.start()
