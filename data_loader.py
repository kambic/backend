import json
import os
from datetime import datetime
from pathlib import Path

import django
from loguru import logger
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()
from django_celery_results.models import TaskResult
from insight.models import Task

mtcms = Path("celery_taskmeta.json")

data = json.loads(mtcms.read_text())

logger.info(f"{len(data)} videos found")
from datetime import datetime, timezone

res = []
for item in tqdm(data, desc="Processing TaskResult", unit="TaskResult"):

    date = item.get("date_done")
    if date:
        date = datetime.fromisoformat(
            date,
        )
        date = date.astimezone(timezone.utc)
    data = {
        "uuid": item.get("task_id"),
        "state": item.get("status"),
        "last_updated": date,
    }

    t = Task.objects.filter(uuid=item.get("task_id")).update(last_updated=date)
