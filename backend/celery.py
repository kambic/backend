import os
import pprint
import random
from time import sleep
from vidra_kit import logger
from vidra_kit.celery_app import get_celery_app

# app = get_celery_app('staging')
# app = get_celery_app('production')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
app = get_celery_app()

# Set the default Django settings module for the 'celery' program.


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # A few settings to speed up inspection
    # worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


@app.task(
    bind=True,
    name="vydra.tasks.cronjob.process_trailer_worker",
    max_retries=3,
    default_retry_delay=5,
)
def dummy_task(self):
    """Simulates fetching data from an unreliable external API with retries."""

    # The 'self' argument is available because bind=True
    attempt = self.request.retries + 1
    url = "https://example.com/api/data"
    logger.info(
        "Attempting to fetch URL: {} (Attempt {}/{})...",
        url,
        attempt,
        self.max_retries + 1,
    )

    try:
        # Simulate network failure 75% of the time on first two attempts
        if attempt <= 2 and random.random() < 0.75:
            raise ConnectionError("Simulated API connection failure.")

        # Simulate success
        sleep(3)
        logger.info("Data successfully fetched from {}", url)
        return {"status": "success", "data_size": 1024}

    except ConnectionError as e:
        # Log the exception, which automatically includes the traceback
        logger.exception("Connection error during fetch. Retrying...")

        # Raise retry to trigger the delay and next attempt
        raise self.retry(exc=e)

    except Exception as e:
        # Log unexpected errors
        logger.error("A critical, non-retryable error occurred.")
        return {"status": "failed", "error": str(e)}
