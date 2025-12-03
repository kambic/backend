# your_project/celery_app/__init__.py

from celery import Celery
import os
import sys
from loguru import logger
from celery.signals import task_prerun, task_postrun

CELERY_CONFIG_ENV = os.environ.get('CELERY_CONFIG_ENV', 'development')


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
