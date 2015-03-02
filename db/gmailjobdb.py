import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
from app.methods import blacklist_email
from userdb import User
from profiledb import Profile
from connectiondb import Connection

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
        return 'GmailJob %s: %s, %s' % (self.id, self.user, self.profile)


    def process(self, gmail_service=None):
        '''
        Each GmailJob is a Profile that this User needs to check to 
        create/update Connection
        Arg: 
            gmail_service must be for self.user!
        '''
        # Authenticate if not provided
        if not gmail_service:
            gmail_service = self.user.get_service(service_type='gmail')
            if not gmail_service:
                logging.info("Could not instantiate authenticated service for %s" % self.user)
                return
        # Process
        self.attempts = self.attempts + 1
        self.save()
        
        c, created_flag = Connection.objects.get_or_create(
            user = self.user,
            profile = self.profile)
        # Updates fields of c by searching through users' entire Gmail inbox 
        c.populate_from_gmail(service=gmail_service)
        self.date_completed = datetime.datetime.now()
        self.save()



