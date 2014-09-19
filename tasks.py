from celery import Celery
from celery.task import periodic_task
from datetime import timedelta
import logging
import settings

celery = Celery('tasks', 
  broker=settings.get('rabbitmq_bigwig_url'))


def add(x, y):
    return x + y

#@celery.task
@periodic_task(run_every=timedelta(seconds=10))
def print_add():
  print add(53, 67)