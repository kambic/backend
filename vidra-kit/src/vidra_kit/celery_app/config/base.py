# celery_app/config/base.py
class BaseConfig:
    timezone = "UTC"
    enable_utc = True
    task_track_started = True
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    worker_prefetch_multiplier = 1
    broker_pool_limit = 1
    broker_heartbeat = 10
    broker_connection_timeout = 5
    worker_max_tasks_per_child = 100
    result_expires = 60 * 60 * 24 * 365
    result_extended = True

    max_workers = 5000
    max_tasks = 10_000

    task_routes = {
        "vydra.tasks.cronjob.process_trailer_worker": {"queue": "trailers_cron"},
    }
