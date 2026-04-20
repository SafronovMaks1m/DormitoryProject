from celery import Celery
from src.celery.bg_tasks import send_messages, send_notifi

celery = Celery(
    "init_celery",
    broker='amqp://guest:guest@rabbitmq:5672/'
)

celery.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True
)

celery.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'src.celery.bg_tasks.send_notifi',
        'schedule': 60.0,
    }
}