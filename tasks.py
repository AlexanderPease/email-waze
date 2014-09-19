from celery import Celery
import celery
import iron_celery

celery = Celery('tasks', broker='ironmq://', backend='ironcache://')

@celery.task
def add(x, y):
    return x + y