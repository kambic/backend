# Create your models here.
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)  # Updated on each save

    class Meta:
        abstract = True  # This model is abstract, no table is created


class TaskState(models.TextChoices):
    """Choices for task execution state."""

    PENDING = "pending", "Pending"
    RECEIVED = "RECEIVED"

    STARTED = "started", "Started"
    SUCCESS = "success", "Success"
    FAILURE = "failure", "Failure"
    REVOKED = "REVOKED", "REVOKED"
    REJECTED = "REJECTED", "REJECTED"
    RETRY = "RETRY", "RETRY"
    IGNORED = "IGNORED", "IGNORED"


class Task(models.Model):
    uuid = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=TaskState)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    retried_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now, null=True, blank=True)

    runtime = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=10
    )

    # Task metadata
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    eta = models.DateTimeField(null=True, blank=True)
    expires = models.DateTimeField(null=True, blank=True)
    retries = models.IntegerField(null=True, blank=True)
    root_id = models.CharField(max_length=255, null=True, blank=True)
    parent_id = models.CharField(max_length=255, null=True, blank=True)
    worker = models.CharField(max_length=255, null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)

    # Store children task IDs as a JSON list
    children = models.JSONField(default=list, blank=True)
    provider = models.ForeignKey(
        "vod.Provider", on_delete=models.SET_NULL, null=True, related_name="tasks"
    )

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["worker"]),
            models.Index(fields=["status"]),
            # models.Index(fields=["task", "status"]),
        ]

    def __str__(self):
        return f"{self.uuid} [{self.status}]"


class TaskEvent(TimestampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=50)
    worker = models.CharField(max_length=100, blank=True, null=True)
    result = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task Event"
        verbose_name_plural = "Task Events"

        # Indexes to speed up common queries
        indexes = [
            models.Index(fields=["worker"]),
            models.Index(fields=["status"]),
            models.Index(fields=["task", "status"]),
        ]

        # Constraints for data integrity
        constraints = [
            # Example: only one "SUCCESS" per task_id
            models.UniqueConstraint(
                fields=["task", "status"],
                condition=models.Q(status="SUCCESS"),
                name="unique_success_per_task",
            ),
        ]

    def __str__(self):
        return f"{self.task} ({self.task_id}) - {self.status}"

    @classmethod
    def new_event(cls, event):
        task_id = event.uuid
        task, created = Task.objects.get_or_create(uuid=task_id)
        if created:
            print(f"Created task {task_id}")

        data = {}
        cls.objects.create(
            task=task,
        )

        return cls(task_id=task_id, **event)


class Workers(models.Model):
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


class Queue(models.Model):
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


class SftpGo(models.Model):
    # Core event info
    event = models.CharField(
        max_length=50, db_index=True, help_text="upload, download, delete, rename, etc."
    )
    username = models.CharField(max_length=255, db_index=True)
    ip = models.GenericIPAddressField(db_index=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(
        max_length=100, blank=True, null=True, help_text="SFTPGo internal user ID"
    )

    # Protocol & paths
    protocol = models.CharField(max_length=20)  # SFTP, FTP, WebDAV, HTTP, etc.
    path = models.TextField(help_text="Full filesystem path on the server")
    virtual_path = models.TextField(help_text="Path as seen by the user")

    # File info
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    object_name = models.TextField(
        blank=True, null=True, help_text="Usually the filename"
    )
    object_type = models.CharField(max_length=50, blank=True, null=True)

    # Status & timing
    status = models.PositiveSmallIntegerField(
        choices=((1, "Success"), (2, "Error")), db_index=True
    )
    timestamp = models.BigIntegerField(
        help_text="SFTPGo nanosecond timestamp (Unix epoch * 1e9 + ns)"
    )
    date = models.DateTimeField(
        db_index=True, help_text="Human-readable ISO datetime from SFTPGo"
    )
    elapsed = models.PositiveIntegerField(
        blank=True, null=True, help_text="Operation time in milliseconds"
    )

    # Flexible fields
    object_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra object data (user/folder JSON when applicable)",
    )
    error = models.TextField(blank=True, null=True)

    # Auto-filled
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "SFTPGo Event"
        verbose_name_plural = "SFTPGo Events"
        indexes = [
            models.Index(fields=["username", "event"]),
            models.Index(fields=["date"]),
            models.Index(fields=["protocol"]),
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.event.upper()} by {self.username} @ {self.date}"

    # Helper: convert SFTPGo nanosecond timestamp → Python datetime
    @property
    def timestamp_datetime(self):
        from datetime import datetime, timedelta

        seconds = self.timestamp // 1_000_000_000
        nanoseconds = self.timestamp % 1_000_000_000
        return datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(
            microseconds=nanoseconds // 1000
        )

    # Optional: save from webhook payload directly
    @classmethod
    def create_from_webhook(cls, payload: dict):
        # Handle empty strings that should be null
        data = payload.copy()
        if data.get("object_data") == "{}":
            data["object_data"] = {}

        elif isinstance(data.get("object_data"), str):
            data["object_data"] = json.loads(data["object_data"])

        # Parse date if not already datetime
        if isinstance(data.get("date"), str):
            # Parse as UTC, then convert to Ljubljana time
            ts = data["date"]

            # Parse string and mark it as UTC
            utc_dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)

            # Convert to your Django TIME_ZONE (Europe/Ljubljana)
            local_dt = dj_tz.localtime(utc_dt)

            data["date"] = local_dt

        return cls.objects.create(**data)


#
