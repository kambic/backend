import json

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from vidra_kit.backends.api import EdgewareApi


import requests
from django.utils.dateparse import parse_datetime
from ...models import Task



class Command(BaseCommand):
    help = "Sync a single Edge + its Streams from API JSON"
    edge_rows = []
    stream_rows = []
    FLOWER_URL = "http://bpl-vidra-03.ts.telekom.si:8080/flower/api/tasks"


    def handle(self, load,  *args, **options):
        print(args,options)
        if load:
            data = self.load_file(load)
        else:
            data = self.get_data()
        self.load_tasks_from_flower(data)

    def add_arguments(self, parser):
        parser.add_argument('--load',type=str)

    def load_tasks_from_flower(self,data):

        with open('tasks.json', 'w') as outfile:
            json.dump(data, outfile)
            self.stdout.write(self.style.SUCCESS(f"Saved tasks.json"))

        for task_data in data:
            # Convert timestamps from string to datetime
            print(task_data)

            task_data = data[task_data]

            for key in [
                "sent", "received", "started", "succeeded",
                "failed", "retried", "revoked", "rejected"
            ]:
                if task_data.get(key):
                    _datetime = task_data[key]
                    print(_datetime)
                    _datetime = str(_datetime)
                    task_data[key] = parse_datetime(_datetime)


            Task.objects.update_or_create(
                id=task_data["uuid"],
                defaults={
                    "type": task_data.get("name"),
                    "state": task_data.get("state"),
                    "sent_at": task_data.get("sent"),
                    "received_at": task_data.get("received"),
                    "started_at": task_data.get("started"),
                    "succeeded_at": task_data.get("succeeded"),
                    "failed_at": task_data.get("failed"),
                    "retried_at": task_data.get("retried"),
                    "revoked_at": task_data.get("revoked"),
                    "rejected_at": task_data.get("rejected"),
                    "runtime": task_data.get("runtime"),
                    "args": str(task_data.get("args")),
                    "kwargs": str(task_data.get("kwargs")),
                    "eta": task_data.get("eta"),
                    "expires": task_data.get("expires"),
                    "retries": task_data.get("retries"),
                    "exchange": task_data.get("exchange"),
                    "routing_key": task_data.get("routing_key"),
                    "root_id": task_data.get("root_id"),
                    "parent_id": task_data.get("parent_id"),
                    "children": task_data.get("children", []),
                    "worker": task_data.get("worker"),
                    "result": str(task_data.get("result")),
                    "exception": str(task_data.get("exception")),
                    "traceback": task_data.get("traceback"),
                },
            )

    def get_data(self):
        response = requests.get(self.FLOWER_URL, auth=('vydra', 'vydra'))
        response.raise_for_status()
        data = response.json()  # list of tasks
        return data

    def load_file(self,file_path):
        with open(file_path) as f:
            data = json.load(f)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(data)} tasks"))
            return data
