import os
import celery
from celery.schedules import crontab
os.environ.setdefault("DJANGO_SETTINGS_MODULE","main.settings")

app = celery.Celery(
    "main",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "set-top-items-every-hour":{
        "task":"accounts.tasks.set_recomend_tops",
        "schedule":crontab(minute=0,hour="*")
    }
}