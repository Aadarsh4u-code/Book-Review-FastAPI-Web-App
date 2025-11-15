celery -A src.worker.celery_app_tasks.celery_app worker --loglevel=INFO &
celery -A src.worker.celery_app_tasks.celery_app flower