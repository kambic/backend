import json
from datetime import datetime, timezone

import requests
from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Task


class Command(BaseCommand):
    help = "Sync a single Edge + its Streams from API JSON"
    edge_rows = []
    stream_rows = []
    FLOWER_URL = "http://bpl-vidra-03.ts.telekom.si:8080/flower/api/tasks"

    def handle(self, load, *args, **options):
        if load:
            data = self.load_file(load)
        else:
            data = self.get_data()
        self.load_tasks_from_flower(data)

    def add_arguments(self, parser):
        parser.add_argument("--load", type=str)

    def load_date(self, date_str):
        try:
            return datetime.fromtimestamp(date_str, timezone.utc).isoformat()
        except:
            return None

    def load_tasks_from_flower(self, data):

        for task_data in tqdm(data, desc="Processing flowers", unit="flower"):

            task_data = data[task_data]

            Task.objects.update_or_create(
                uuid=task_data["uuid"],
                defaults={
                    "status": task_data.get("state"),
                    "sent_at": self.load_date(task_data.get("sent")),
                    "received_at": self.load_date(task_data.get("received")),
                    "started_at": self.load_date(task_data.get("started")),
                    "succeeded_at": self.load_date(task_data.get("succeeded")),
                    "failed_at": self.load_date(task_data.get("failed")),
                    "retried_at": self.load_date(task_data.get("retried")),
                    "revoked_at": self.load_date(task_data.get("revoked")),
                    "rejected_at": self.load_date(task_data.get("rejected")),
                    "root_id": task_data.get("root_id"),
                    "parent_id": task_data.get("parent_id"),
                    "children": task_data.get("children", []),
                },
            )

    def get_data(self):
        response = requests.get(self.FLOWER_URL, auth=("vydra", "vydra"))
        response.raise_for_status()
        data = response.json()  # list of tasks
        return data

    def load_file(self, file_path):
        with open(file_path) as f:
            data = json.load(f)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(data)} tasks"))
            return data
