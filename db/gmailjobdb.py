import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
from app.methods import blacklist_email
from userdb import User
from profiledb import Profile

mongo_database = settings.get('mongo_database')
connect('gmailmessagejob', host=mongo_database['host'])

class GmailJob(Document):
    '''
    A Profile to be checked for a given User
    to update Connections database. 

    These are created by checking a GmailMessageJob. The worker then uses this
    GmailJob to query the Gmail API directly about this address. 
    '''
    user = ReferenceField(User, required=True)
    profile = ReferenceField(Profile, required=True)

    # Date this job was created and completed
    date_added = DateTimeField(default=datetime.datetime.now(), required=True)
    date_completed = DateTimeField()

    # Track number of attempts made to check this Gmail for updating db
    attempts = IntField(default=0) 

    def __str__(self):
        return 'GmailJob %s: %s, profile %s' % (self.id, self.user, self.profile)





