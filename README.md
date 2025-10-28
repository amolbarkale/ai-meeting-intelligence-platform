docker run -d -p 6379:6379 redis

uvicorn app.main:app --reload

celery -A worker.celery_app worker --loglevel=info -P eventlet