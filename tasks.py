from celery import Celery
from celery.decorators import periodic_task
from datetime import timedelta
import logging
import settings

from scripts.google_contacts_job import main as google_contacts_job

from db.userdb import User
from app.gmail import GmailJob

app = Celery('tasks', 
    broker=settings.get('rabbitmq_bigwig_url'),
    backend='amqp')

@app.task
def add(x, y):
    return x + y

@periodic_task(run_every=timedelta(hours=24))
def run_google_contacts_job():
    logging.info("Celery worker starting tasks.run_google_contacts_job()")
    google_contacts_job()
    logging.info("Celery worker finished tasks.run_google_contacts_job()")

@app.task
def run_gmail_job():
    logging.info("Celery worker starting tasks.run_gmail_job()")

    # Run jobs on all users that are brand new first...
    for u in User.objects():
        if not u.gmail_job.success:
            logging.info("Starting GmailJob for new User %s" % u)
            GmailJob(u)

    # ...then updates existing users
    for u in User.objects():
        logging.info("Starting GmailJob for existing User %s" % u)
        GmailJob(u)

    logging.info("Celery worker finished tasks.run_gmail_job()")