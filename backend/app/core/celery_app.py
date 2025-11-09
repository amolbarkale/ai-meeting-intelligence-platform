import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=celery_broker_url,
    backend=celery_result_backend,
    include=["app.services.processing_service"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
    task_retry_jitter=True,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=100,
)
