import os
import celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE","main.settings")

app = celery.Celery(
    "main",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

app.autodiscover_tasks()