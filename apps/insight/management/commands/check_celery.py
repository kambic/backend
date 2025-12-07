from django.core.management.base import BaseCommand

from vidra_kit.celery_app.celery_manager import CeleryManager
from vidra_kit.celery_app import get_celery_app
from vidra_kit.celery_app.celery_monitor import CeleryMonitor


class Command(BaseCommand):
    help = 'Check Celery workers and queues'

    def handle(self, *args, **options):
        apps = [get_celery_app('production'), get_celery_app('staging')]

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

        stats = manager.get_workers()
