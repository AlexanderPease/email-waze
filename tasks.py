import celery
from datetime import timedelta
import logging
import settings
from scripts.google_contacts_job import main as google_contacts_job
from scripts.gmail_job import main as gmail_job

celery = celery.Celery('tasks', 
    broker=settings.get('rabbitmq_bigwig_url'))


def add(x, y):
    return x + y

#@celery.task.periodic_task(run_every=timedelta(seconds=10))
@celery.task
def run_google_contacts_job():
    logging.info("Celery worker starting tasks.run_google_contacts_job()")
    google_contacts_job()
    logging.info("Celery worker finished tasks.run_google_contacts_job()")

@celery.task
def run_gmail_job():
    logging.info("Celery worker starting tasks.run_mail_job()")
    gmail_job()
    logging.info("Celery worker finished tasks.run_mail_job()")