import json
from pathlib import Path

expired:list[dict] = json.loads(Path("mtcms-prod-response.json").read_text())


for item in expired:
    print(item.items())
