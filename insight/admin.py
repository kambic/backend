from django.contrib import admin,messages

from vidra_kit.celery_app.celery_manager import CeleryManager
from .models import Task, TaskResult, ActiveTaskRecord, QueueStatus, WorkerStatus


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "state",
        "worker",
        "sent_at",
        "started_at",
        "succeeded_at",
        "failed_at",
        "runtime",
    )
    list_filter = ("state", "worker")
    search_fields = ("id", "type", "worker", "root_id", "parent_id")
    readonly_fields = (
        "id",
        "sent_at",
        "received_at",
        "started_at",
        "succeeded_at",
        "failed_at",
        "retried_at",
        "revoked_at",
        "rejected_at",
        "last_updated",
        "runtime",
    )
    fieldsets = (
        ("Basic Info", {"fields": ("id", "type", "state", "worker")}),
        ("Timing", {
            "fields": (
                "sent_at",
                "received_at",
                "started_at",
                "succeeded_at",
                "failed_at",
                "retried_at",
                "revoked_at",
                "rejected_at",
                "last_updated",
                "runtime",
            )
        }),
        ("Task Data", {
            "fields": ("args", "kwargs", "eta", "expires", "retries", "exchange", "routing_key")
        }),
        ("Hierarchy", {"fields": ("root_id", "parent_id", "children")}),
        ("Result / Exception", {"fields": ("result", "exception", "traceback")}),
    )
    ordering = ("-sent_at",)


@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "state", "worker", "queue", "ignored", "retries")
    list_filter = ("state", "worker", "queue", "ignored")
    search_fields = ("id", "type", "worker")
    readonly_fields = ("id", "created_at", "updated_at", "args", "kwargs", "traceback")
    fieldsets = (
        ("Basic Info", {"fields": ("id", "type", "state", "queue", "worker", "ignored")}),
        ("Args / Kwargs", {"fields": ("args", "kwargs")}),
        ("Result / Traceback", {"fields": ("result", "traceback")}),
        ("Retries", {"fields": ("retries",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    ordering = ("-created_at",)



# Django Admin Configurations
@admin.register(WorkerStatus)
class WorkerStatusAdmin(admin.ModelAdmin):
    """
    Admin interface for WorkerStatus with custom actions for management.
    """

    list_display = ('hostname', 'is_active', 'state', 'active_concurrency', 'total_processed', 'total_failed', 'load_avg', 'last_updated')
    list_filter = ('is_active', 'state', 'last_updated')
    search_fields = ('hostname',)
    readonly_fields = ('last_updated', 'last_ping')

    actions = ['restart_selected_workers', 'shutdown_selected_workers', 'autoscale_selected_workers', 'grow_pool_selected', 'shrink_pool_selected']

    def restart_selected_workers(self, request, queryset):
        """
        Action to restart selected workers.
        """
        manager = CeleryManager(app)
        hostnames = [f"celery@{obj.hostname}" for obj in queryset]  # Assuming Celery hostname format
        replies = manager.restart_workers(destination=hostnames, update_orm_after=True)
        if replies:
            self.message_user(request, f"Restarted {len(queryset)} workers. Replies: {replies}", messages.SUCCESS)
        else:
            self.message_user(request, f"Failed to restart {len(queryset)} workers.", messages.ERROR)

    restart_selected_workers.short_description = "Restart selected workers (pool restart)"

    def shutdown_selected_workers(self, request, queryset):
        """
        Action to shutdown selected workers.
        """
        manager = CeleryManager(app)
        hostnames = [f"celery@{obj.hostname}" for obj in queryset]
        replies = manager.shutdown_workers(destination=hostnames, update_orm_after=True)
        if replies:
            self.message_user(request, f"Shutdown initiated for {len(queryset)} workers. Replies: {replies}", messages.WARNING)
        else:
            self.message_user(request, f"Failed to shutdown {len(queryset)} workers.", messages.ERROR)

    shutdown_selected_workers.short_description = "Gracefully shutdown selected workers"

    def autoscale_selected_workers(self, request, queryset):
        """
        Action to autoscale selected workers (prompt for min/max via change form or hardcode for simplicity).
        For simplicity, hardcoded to 2-8; enhance with inline form if needed.
        """
        if len(queryset) != 1:
            self.message_user(request, "Please select exactly one worker for autoscaling.", messages.ERROR)
            return
        manager = CeleryManager(app)
        hostname = f"celery@{queryset[0].hostname}"
        replies = manager.autoscale_workers(min_workers=2, max_workers=8, destination=[hostname])
        if replies:
            self.message_user(request, f"Autoscaled worker {queryset[0].hostname} to 2-8. Replies: {replies}", messages.SUCCESS)
        else:
            self.message_user(request, f"Failed to autoscale worker {queryset[0].hostname}.", messages.ERROR)

    autoscale_selected_workers.short_description = "Autoscale selected worker (min=2, max=8)"

    def grow_pool_selected(self, request, queryset):
        """
        Action to grow pool of selected workers by 1.
        """
        manager = CeleryManager(app)
        hostnames = [f"celery@{obj.hostname}" for obj in queryset]
        replies = manager.grow_pool(n=1, destination=hostnames)
        if replies:
            self.message_user(request, f"Grew pool by 1 for {len(queryset)} workers. Replies: {replies}", messages.SUCCESS)
        else:
            self.message_user(request, f"Failed to grow pool for {len(queryset)} workers.", messages.ERROR)

    grow_pool_selected.short_description = "Grow pool by 1 for selected workers"

    def shrink_pool_selected(self, request, queryset):
        """
        Action to shrink pool of selected workers by 1.
        """
        manager = CeleryManager(app)
        hostnames = [f"celery@{obj.hostname}" for obj in queryset]
        replies = manager.shrink_pool(n=1, destination=hostnames)
        if replies:
            self.message_user(request, f"Shrunk pool by 1 for {len(queryset)} workers. Replies: {replies}", messages.SUCCESS)
        else:
            self.message_user(request, f"Failed to shrink pool for {len(queryset)} workers.", messages.ERROR)

    shrink_pool_selected.short_description = "Shrink pool by 1 for selected workers"


@admin.register(QueueStatus)
class QueueStatusAdmin(admin.ModelAdmin):
    """
    Admin interface for QueueStatus with custom actions.
    """

    list_display = ('name', 'total_messages', 'consumers', 'state', 'last_updated')
    list_filter = ('state', 'last_updated')
    search_fields = ('name',)
    readonly_fields = ('last_updated',)

    actions = ['purge_all_queues']

    def purge_all_queues(self, request, queryset):
        """
        Action to purge all queues (global).
        """
        manager = CeleryManager(app)
        purged_count = manager.purge_tasks()
        self.message_user(request, f"Purged {purged_count} tasks from all queues.", messages.WARNING)
        # Refresh queue statuses
        manager.get_active_queues(update_orm=True)

    purge_all_queues.short_description = "Purge all waiting tasks from queues"


@admin.register(ActiveTaskRecord)
class ActiveTaskRecordAdmin(admin.ModelAdmin):
    """
    Admin interface for ActiveTaskRecord with custom actions.
    """

    list_display = ('task_id', 'name', 'worker_hostname', 'status', 'last_seen')
    list_filter = ('status', 'worker_hostname', 'last_seen')
    search_fields = ('task_id', 'name')
    readonly_fields = ('started_at', 'last_seen')

    actions = ['revoke_selected_tasks', 'mark_as_completed']

    def revoke_selected_tasks(self, request, queryset):
        """
        Action to revoke selected active tasks.
        """
        task_ids = [obj.task_id for obj in queryset if obj.status == 'active']
        if not task_ids:
            self.message_user(request, "No active tasks selected for revocation.", messages.ERROR)
            return
        manager = CeleryManager(app)
        replies = manager.revoke_task(task_id=task_ids, terminate=False)
        if replies:
            self.message_user(request, f"Revoked {len(task_ids)} tasks. Replies: {replies}", messages.SUCCESS)
        else:
            self.message_user(request, f"Failed to revoke {len(task_ids)} tasks.", messages.ERROR)

    revoke_selected_tasks.short_description = "Revoke selected active tasks (non-terminating)"

    def mark_as_completed(self, request, queryset):
        """
        Action to manually mark tasks as completed.
        """
        updated = queryset.update(status='completed')
        self.message_user(request, f"Marked {updated} tasks as completed.", messages.SUCCESS)

    mark_as_completed.short_description = "Mark selected tasks as completed"
