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
    A Gmail address (and possibly name) to be checked for a given User
    to update Connections database. 

    Updating/creating Profile is done in tasks.py. A GmailJob without a name may not
    be added to connectiondb b/c no Profile exists. This happens when an email 
    comes in without a name, but we still want to check global database to see if 
    a name exists for that email address. 

    These are created by checking a GmailMessageJob. The worker then uses this
    GmailJob to query the Gmail API directly about this address. 

    If just an email is supplied, then only preexisting Connections can be updated.
    If both an email and name are supplied, then new Profiles and Connections
    can be created.
    '''
    user = ReferenceField(User, required=True)
    email = StringField(required=True, unique_with='user')

    # Only include a User if this 
    name = StringField()

    # Date this job was created and completed
    date_added = DateTimeField(default=datetime.datetime.now(), required=True)
    date_completed = DateTimeField()

    # Track number of attempts made to check this Gmail for updating db
    attempts = IntField(default=0) 

    def save(self , *args, **kwargs):
        '''
        Only saves a GmailJob if the email is worth checking.
        This is quality control filtering. 
        '''
        if not blacklist_email(self.email):
            return super(GmailJob, self).save(*args, **kwargs)

    def __str__(self):
        return 'GmailJob: %s, email %s, name %s' % (self.user, self.email, self.name)





