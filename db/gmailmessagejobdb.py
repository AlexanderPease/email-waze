import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
from userdb import User

mongo_database = settings.get('mongo_database')
connect('gmailmessagejob', host=mongo_database['host'])

class GmailMessageJob(Document):
    '''
    A Gmail message which needs to be checked to update Profile and Connection
    databases. Think of these as atomic jobs that the worker should run. 
    '''
    user = ReferenceField(User, required=True)

    # The unique ID identifying the Gmail message and thread for this user
    message_id = StringField(required=True, unique_with='user')
    thread_id = StringField() # not currently used

    # Date this job was created and completed
    date_added = DateTimeField(default=datetime.datetime.now(), required=True)
    date_completed = DateTimeField()

    # Track number of attempts made to check this Gmail for updating db
    attempts = IntField(default=0) 

    def __str__(self):
        return 'GmailMessageJob: %s, message id %s' % (self.user, self.message_id)





