from celery import Celery

celery = Celery(
    "init_celery",
    broker='amqp://guest:guest@localhost:5672/',
    
)

celery.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True
)

celery.conf.beat_schedule = {
    'run-me-background-task': {
        'task': 'sending_notifications.send_notifi',
        'schedule': 60.0,
    }
}