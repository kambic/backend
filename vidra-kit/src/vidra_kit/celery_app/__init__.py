from celery import Celery
import os
from celery.signals import task_prerun, task_postrun

CELERY_CONFIG_ENV = os.environ.get("CELERY_CONFIG_ENV", "development")
from vidra_kit import logger


@task_prerun.connect
def on_task_prerun(task_id=None, task=None, **kwargs):
    """Fired before a task executes. Binds task info to Loguru context."""
    # Use logger.patch to add task info to the context
    logger.info("Celery task started.")


@task_postrun.connect
def on_task_postrun(task_id=None, task=None, **kwargs):
    """Fired after a task executes. Logs task finish and context is implicitly cleared."""
    logger.info("Celery task finished.")


def get_celery_app(env=None):
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
    celery_app.autodiscover_tasks(["vidra_kit.celery_app"], related_name="tasks")

    return celery_app


# --- 5. Application Instances ---

# The default application instance used by the 'celery' command line tool
# e.g., celery -A celery_app worker
# app = get_celery_app()

# Explicitly create other environment apps for potential testing or explicit binding
# These are optional, as the primary 'app' handles the environment determined by CELERY_CONFIG_ENV
# app_dev = make_celery(env='development')
# app_staging = make_celery(env='staging')
# app_prod = make_celery(env='production')
