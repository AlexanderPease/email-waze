from celery import Celery
import iron_celery

celery = Celery('tasks', broker='ironmq://', backend='ironcache://')
#celery = Celery('tasks',
#          broker='ironmq://541b41d38c13d400090000b7:9xUFw7vOecwvzeta00QFq0cTb4Y@', 
#          backend='ironcache://541b41e4de859900090000a1:xWVAtE8kH17YJkXpRCpvMhBKZFE@')
          #broker='amqp://tmkV1N30:ycxSvqEgiRMa5mLVWOC1kfCic7KVuyaX@skinny-dandelion-18.bigwig.lshift.net:10846/ns-7HzsJzDJU') 

@celery.task
def add(x, y):
    return x + y