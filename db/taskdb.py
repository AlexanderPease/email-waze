import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
from userdb import User

mongo_database = settings.get('mongo_database')
connect('task', host=mongo_database['host'])

class Task(Document):
    name = StringField(required=True)
    start = DateTimeField(required=True, default=datetime.datetime.now())
    end = DateTimeField()
    num_users = IntField(default=0) # count number of users attempted
    num_users_completed = IntField(default=0) # count number of users attempted
    user = ReferenceField(User) # if task is about a single user


