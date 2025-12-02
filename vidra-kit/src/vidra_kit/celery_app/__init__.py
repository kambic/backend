# your_project/celery_app/__init__.py

from celery import Celery
import os
import sys
from loguru import logger
from celery.signals import task_prerun, task_postrun

# --- 1. Environment and Configuration Setup ---

# Define the environment key for configuration selection
# Defaults to 'development' if CELERY_CONFIG_ENV is not set
CELERY_CONFIG_ENV = os.environ.get('CELERY_CONFIG_ENV', 'development')


# --- 2. Loguru Configuration ---

def setup_loguru(env: str):
    """Configures Loguru handlers and format based on the environment."""

    # Remove default Loguru handler to take full control
    logger.remove()

    # Define the log format string to include context variables from logger.bind()
    # {extra[task_name]} and {extra[task_id]} are added by the signal handlers below
    LOG_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[task_name]: <25}</cyan> | "
        "<yellow>{extra[task_id]: <36}</yellow> | "
        "{message}"
    )

    # Default logging level for console output
    console_level = "INFO"
    file_level = "WARNING"

    if env == 'production':
        console_level = "WARNING"
        file_level = "ERROR"

    # 1. Console/Stderr Sink (always active for immediate feedback)
    logger.add(
        sys.stderr,
        level=console_level,
        colorize=True if env == 'development' else False,
        format=LOG_FORMAT
    )

    # 2. File Sink (for Staging and Production reliability)
    if env in ['staging', 'production']:
        logger.add(
            f"logs/{env}_celery.log",
            rotation="100 MB",
            compression="zip",
            level=file_level,
            format=LOG_FORMAT
        )

    # 3. Redirect Internal Celery Logging: Captures Celery's built-in print/warnings/errors
    # Note: This sink doesn't use the full LOG_FORMAT as internal Celery messages
    # often lack the task context.
    logger.add(
        lambda msg: sys.__stderr__.write(msg.record["message"] + "\n"),
        level="WARNING",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>Celery Internal:</cyan> {message}"
    )


# --- 3. Celery Signal Handlers for Log Context ---

@task_prerun.connect
def on_task_prerun(task_id=None, task=None, **kwargs):
    """Fired before a task executes. Binds task info to Loguru context."""
    # Use logger.patch to add task info to the context
    logger.patch(lambda record: record["extra"].update(task_id=task_id, task_name=task.name)).info(
        "Celery task started.")


@task_postrun.connect
def on_task_postrun(task_id=None, task=None, **kwargs):
    """Fired after a task executes. Logs task finish and context is implicitly cleared."""
    logger.patch(lambda record: record["extra"].update(task_id=task_id, task_name=task.name)).info(
        "Celery task finished.")
    # Context is thread-local and will automatically clear for the next task run


# --- 4. The Main Celery Factory ---

def make_celery(env=None):
    """
    Creates and configures a Celery application based on the given environment.
    """
    env = env or CELERY_CONFIG_ENV

    full_module_path = f"vidra_kit.celery_app.config.{env}"
    try:

        config_module = __import__(full_module_path, fromlist=["Config"])
        Config = config_module.Config

    except ImportError as e:
        # Re-raising the error with more context
        raise ValueError(
            f"Configuration import failed for environment '{env}'. "
            f"Tried to import '{full_module_path}'. "
            f"Original error: {e}"
        )
    # 2. Initialize and configure Celery
    celery_app = Celery("vidra_kit")
    celery_app.config_from_object(Config)

    # Find tasks in the specified package
    # celery_app.autodiscover_tasks(["celery_app"], related_name='tasks')
    celery_app.autodiscover_tasks(["vidra_kit.celery_app"], related_name='tasks')

    # 3. Setup Logging
    setup_loguru(env)

    return celery_app


# --- 5. Application Instances ---

# The default application instance used by the 'celery' command line tool
# e.g., celery -A celery_app worker
app = make_celery()

# Explicitly create other environment apps for potential testing or explicit binding
# These are optional, as the primary 'app' handles the environment determined by CELERY_CONFIG_ENV
# app_dev = make_celery(env='development')
# app_staging = make_celery(env='staging')
# app_prod = make_celery(env='production')
