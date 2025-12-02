# celery_app/config/staging.py
from .base import BaseConfig

class Config(BaseConfig):
    result_backend = "redis://localhost:6379/0"
    broker_url = "redis://localhost:6379/1"
