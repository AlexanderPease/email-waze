import settings, logging
from mongoengine import *

mongo_database = settings.get('mongo_database')
connect('stats', host=mongo_database['host'])

class Stats(Document):
    """
    Document to track basic statistics using a background job
    """
    date = DateTimeField(required=True)
    profiles = IntField()
    connections = IntField()
    users = IntField()
    groups = IntField()

    def __str__(self):
        return "Stats from %s" % self.date




