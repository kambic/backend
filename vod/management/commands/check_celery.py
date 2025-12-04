from django.core.management.base import BaseCommand

from vidra_kit.celery_app.celery_manager import CeleryManager
from ...models import ActiveTaskRecord
from vidra_kit.celery_app.app import celery_apps
from vidra_kit.celery_app.celery_monitor import CeleryMonitor


class Command(BaseCommand):
    help = 'Check Celery workers and queues'

    def handle(self, *args, **options):
        apps = celery_apps(flat=True)

        for app in apps:
            try:
                self.manager(app)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error checking {e}"))
                # self.stderr.write(f"Error checking {app.name}")

    def check_celery(self, app):
        monitor = CeleryMonitor(app=app)
        workers = monitor.get_workers_status()
        queues = monitor.get_queue_infos()
        # print(f"Workers: {workers}")
        # print(f"Queues: {queues}")

        # for q in queues:
        #     app.control.cancel_consumer(q)

    def manager(self, app):

        manager = CeleryManager(app)  # Pass your Celery app

        stats = manager.get_worker_stats(update_orm=True)
        for hostname, stat in stats.items():
            print(f"Updated {hostname}: {stat.processed} processed, load {stat.load}")

        workers = manager.get_worker_overview(update_orm=True)  # Fetch from DB
        for worker in workers:
            print(f"Hostname: {worker.hostname}, Active: {worker.active}")
            if worker.stats:
                print(f"  Processed: {worker.stats.processed}, Failed: {worker.stats.failed}")

        queues = manager.get_active_queues(update_orm=True)

        # Example 4: Revoke task and update status in ORM
        print("\nRevoking task and updating status:")
        # replies = manager.revoke_task(task_id="example-task-id")
        # # Check ORM
        # task = ActiveTaskRecord.objects.filter(task_id="example-task-id").first()
        # if task:
        #     print(f"Task status updated to: {task.status}")
        #
        # # Example 5: Management with post-update
        # print("\nRestarting workers and updating statuses:")
        # replies = manager.restart_workers(update_orm_after=True)
        # if replies:
        #     print("Restart replies:", replies)
