from celery import Celery
import celery
import iron_celery
import settings

celery = Celery('tasks', 
  broker=settings.get('rabbitmq_bigwig_url'))

@celery.task
def add(x, y):
    return x + y