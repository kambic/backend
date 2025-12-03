# Create your models here.
from django.db import models
from django.utils import timezone


class TaskState(models.TextChoices):
    """Choices for task execution state."""

    PENDING = 'pending', 'Pending'
    RECEIVED = "RECEIVED"

    STARTED = 'started', 'Started'
    SUCCESS = 'success', 'Success'
    FAILURE = 'failure', 'Failure'
    REVOKED = "REVOKED", "REVOKED"
    REJECTED = "REJECTED", "REJECTED"
    RETRY = "RETRY" ,"RETRY"
    IGNORED = "IGNORED", "IGNORED"


class Task(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=20, choices=TaskState)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    retried_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)

    runtime = models.FloatField(null=True, blank=True)

    # Task metadata
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    eta = models.DateTimeField(null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    retries = models.IntegerField(null=True, blank=True)
    exchange = models.CharField(max_length=255, null=True, blank=True)
    routing_key = models.CharField(max_length=255, null=True, blank=True)
    root_id = models.CharField(max_length=255, null=True, blank=True)
    parent_id = models.CharField(max_length=255, null=True, blank=True)
    worker = models.CharField(max_length=255, null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)

    # Store children task IDs as a JSON list
    children = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.id} [{self.state}]"


class TaskResult(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=20, choices=TaskState)
    queue = models.CharField(max_length=255, null=True, blank=True)

    result = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)
    ignored = models.BooleanField(default=False)

    # Store args and kwargs as JSON
    args = models.JSONField(default=list, blank=True)
    kwargs = models.JSONField(default=dict, blank=True)

    retries = models.IntegerField(default=0)
    worker = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # If result is an Exception object, store its repr
        if isinstance(self.result, Exception):
            self.result = repr(self.result)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} [{self.state}]"



class WorkerStatus(models.Model):
    """
    Django model to store worker status and statistics.
    """

    hostname = models.CharField(max_length=255, unique=True)
    pid = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=50, default="unknown")
    is_active = models.BooleanField(default=False)
    active_concurrency = models.IntegerField(default=0)
    total_processed = models.BigIntegerField(default=0)
    total_cancelled = models.BigIntegerField(default=0)
    total_failed = models.BigIntegerField(default=0)
    load_avg = models.FloatField(default=0.0)
    prefetch_count = models.IntegerField(default=0)
    uptime_seconds = models.IntegerField(default=0)
    pool_type = models.CharField(max_length=50, default="")
    max_tasks_per_child = models.CharField(max_length=50, null=True, blank=True)
    max_memory_per_child = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_ping = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["hostname"]

    def __str__(self):
        return f"{self.hostname} ({self.state})"


class QueueStatus(models.Model):
    """
    Django model to store queue status.
    """

    name = models.CharField(max_length=255, unique=True)
    messages_ready = models.IntegerField(default=0)
    messages_unacknowledged = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    consumers = models.IntegerField(default=0)
    state = models.CharField(max_length=50, default="running")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.total_messages} msgs)"


class ActiveTaskRecord(models.Model):
    """
    Django model to record active tasks (for monitoring; may need cleanup).
    """

    task_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    args = models.JSONField(default=list)
    kwargs = models.JSONField(default=dict)
    worker_hostname = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default="active")

    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):
        return f"{self.name}@{self.worker_hostname} ({self.task_id})"
