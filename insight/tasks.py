from vidra_kit.celery_app.__init__ import app  # Import the Celery app
from loguru import logger


@app.task(bind=True)
def my_long_running_task(self, data):
    # Loguru automatically includes the time, level, and file/line
    logger.info("Task starting for data: {}", data)

    try:
        # Simulate work
        # ...

        # Log at the DEBUG level (if enabled in your config)
        logger.debug("Intermediate step complete.")

        return "Task finished"

    except Exception as e:
        # Loguru's .exception() automatically includes the full traceback
        # and the log level is set to ERROR.
        logger.exception("An error occurred during task execution.")
        # Reraise or handle the exception to mark the task as failed
        raise self.retry(exc=e, countdown=5, max_retries=3)
