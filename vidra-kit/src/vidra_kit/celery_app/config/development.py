# celery_app/config/staging.py
from .base import BaseConfig


class Config(BaseConfig):
    broker_url = "amqp://guest:guest@bpl-vidra-03.ts.telekom.si:5672/celery"
    result_backend = "django-db"
