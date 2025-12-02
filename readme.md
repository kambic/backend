# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 20,
        },
    }
}

Then run once:

PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
https://github.com/danyi1212/celery-insights/tree/main
