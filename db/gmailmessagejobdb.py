import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
from email.utils import parseaddr
from app.methods import blacklist_email
import app.gmail as gmail
from userdb import User
from profiledb import Profile
from gmailjobdb import GmailJob

mongo_database = settings.get('mongo_database')
connect('gmailmessagejob', host=mongo_database['host'])

# Which header to check
HEADER_LIST = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc'] 

class GmailMessageJob(Document):
    '''
    A Gmail message which needs to be checked to update Profile and Connection
    databases. Think of these as atomic jobs that the worker should run. 
    '''
    user = ReferenceField(User, required=True)

    # The unique ID identifying the Gmail message and thread for this user
    message_id = StringField(required=True)
    thread_id = StringField() # not currently used

    # Date this job was created and completed
    date_added = DateTimeField(default=datetime.datetime.now(), required=True)
    date_completed = DateTimeField()

    # Track number of attempts made to check this Gmail for updating db
    attempts = IntField(default=0) 

    # Save headers of this message when processed
    header = DictField()

    def __str__(self):
        return 'GmailMessageJob: %s, message id %s' % (self.user, self.message_id)

    def process(self, gmail_service=None):
        '''
        Checks the email of this GmailMessageJob to create all Profiles, and 
        create/update Connections between that Profile and User. 

        Args:
            gmail_service: Must be the gmail object for the User of this job
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
        logging.info("Checking message of id: %s" % self.message_id)
        msg = gmail.GetMessage(gmail_service, 'me', self.message_id)
        msg_header_all = gmail.GetMessageHeader(msg)
        logging.info(msg_header_all)
        if msg_header_all:
            self.header = msg_header_all
            self.save()
            for header_string in HEADER_LIST:
                if header_string in msg_header_all.keys():
                    msg_header = msg_header_all[header_string]
                    msg_header_parts = msg_header.split(', ') # Comma-delimited for multiple emails in same header field
                    for msg_header_part in msg_header_parts:
                        field = parseaddr(msg_header_part) # Allows local emails addresses unfortunately
                        name = field[0]
                        email = field[1]
                        logging.info('%s, %s' % (name, email))

                        if email and email is not "" and not blacklist_email(email):
                            try:
                                p = Profile.objects.get(email=email)
                            except:
                                p = Profile.add_new(name=name, email=email) # Profile must have a name to be created

                            # Add/update Connection if not Cc field or to oneself
                            if p and header_string != 'Cc' and self.user.email != p.email:
                                logging.info('creating for %s' % p)
                                gmail_job, created_flag = GmailJob.objects.get_or_create(
                                    user = self.user,
                                    profile = p, 
                                    date_completed__exists = False)
                                if created_flag:
                                    logging.info(gmail_job)

            self.date_completed = datetime.datetime.now()
            self.save()



