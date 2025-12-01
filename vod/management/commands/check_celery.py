from django.core.management.base import BaseCommand

from ...models import Worker
from vidra_kit.celery_app.app import celery_apps
from vidra_kit.celery_app.celery_monitor import CeleryMonitor


class Command(BaseCommand):
    help = 'Check Celery workers and queues'

    def handle(self, *args, **options):
        apps = celery_apps(flat=True)

        for app in apps:
            self.check_celery(app)

    def check_celery(self, app):
        monitor = CeleryMonitor(app=app)
        workers = monitor.get_workers_status()
        queues = monitor.get_queue_infos()
        # print(f"Workers: {workers}")
        # print(f"Queues: {queues}")

        # for q in queues:
        #     app.control.cancel_consumer(q)

        for worker in workers:
            w = Worker.objects.get_or_create(name=worker.name)[0]
            w.processed_tasks = worker.processed_tasks
            w.uptime = worker.uptime
            w.is_alive = worker.is_alive
            w.active_tasks = worker.active_tasks
            w.save()
