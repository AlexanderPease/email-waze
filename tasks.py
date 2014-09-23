from celery import Celery
from celery.decorators import periodic_task
from datetime import timedelta
import logging
import settings

from scripts.google_contacts_job import main as google_contacts_job

from db.userdb import User
from app.gmail import GmailJob

celery_worker = Celery('tasks', 
    broker=settings.get('rabbitmq_bigwig_url'),
    backend='amqp')

@celery_worker.task
def add(x, y):
    return x + y

@periodic_task(run_every=timedelta(hours=24))
def run_google_contacts_job():
    logging.info("Celery worker starting tasks.run_google_contacts_job()")
    google_contacts_job()
    logging.info("Celery worker finished tasks.run_google_contacts_job()")

@celery_worker.task
def run_gmail_job():
    logging.info("Celery worker starting tasks.run_gmail_job()")
    for u in User.objects():
        # Run jobs on all users that are brand new
        if not u.gmail_job.success:
            logging.info("Starting GmailJob for %s" % u)
            GmailJob(u)
    logging.info("Celery worker finished tasks.run_gmail_job()")