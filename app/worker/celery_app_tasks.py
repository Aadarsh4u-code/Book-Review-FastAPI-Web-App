from typing import List

from celery import Celery
from asgiref.sync import async_to_sync

from app.worker.email_tasks import create_email_message, fastmail

celery_app = Celery()

celery_app.config_from_object('app.core.config')

@celery_app.task()
def send_email_task(*, recipient_email: List[str], subject: str, html_body: str):
    message = create_email_message(
        recipient=recipient_email,
        subject=subject,
        body=html_body,
    )
    # Run async functions inside Celery tasks because Celery workers run in a synchronous environment.
    async_to_sync(fastmail.send_message)(message)
    print("Email sent successfully")


# Command to run Celery in terminal
# celery -A app.worker.celery_app_tasks.celery_app worker