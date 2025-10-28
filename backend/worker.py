import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Get the broker URL from the environment variable we set in .env
celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize the Celery app
celery_app = Celery(
    "tasks",
    broker=celery_broker_url,
    backend=celery_result_backend,
    include=["app.services.processing_service"] # IMPORTANT: This tells Celery where to find tasks
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    task_retry_jitter=True,
)