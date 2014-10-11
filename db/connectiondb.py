import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
import logging, datetime
from app import gmail

mongo_database = settings.get('mongo_database')
connect('connection', host=mongo_database['host'])


class Connection(Document):
    # The User who has corresponded with... 
    user = ReferenceField(User, required=True)

    # ...the email address of this Profile
    profile = ReferenceField(Profile, required=True) 

    total_emails_in = IntField()
    total_emails_out = IntField()
    latest_email_in_date = DateTimeField()
    latest_email_out_date = DateTimeField()

    # Last time a job was run that updated this document
    # Jobs should be User-first
    last_updated = DateTimeField()

    # Compound index so that pair of self.user and self.profile must be unique
    meta = {
        'indexes': [
            {'fields': ['user', 'profile'], 'unique': True},
        ]
    }


    def __str__(self):
        return 'Connection: User %s <-> Profile %s' % (self.user, self.profile)


    def populate_from_gmail(self, service):
        """
        This function searches entire inbox to populate fields,
        therefore it is not optimized for speed. Only looks for messages directly
        to: and from: User and Profile.

        Requires service to be from self.user, or else will populate
        field incorrectly. 

        Args:
            service: a Gmail API service object authed in with self.user
        """
        # See if any messages match query
        in_query = "from:%s to:%s" % (self.profile.email, self.user.email)
        emails_in = gmail.ListMessagesMatchingQuery(service=service, 
                                                    user_id='me', 
                                                    query=in_query)
        out_query = "to:%s from:%s" % (self.profile.email, self.user.email) 
        emails_out = gmail.ListMessagesMatchingQuery(service=service, 
                                                    user_id='me', 
                                                    query=out_query)

        # Emails in fields
        if emails_in and len(emails_in) > 0:
            self.total_emails_in = len(emails_in)

            # Get dates of latest emails in and out
            try:
                latest_email_in = gmail.GetMessage(service=service, 
                                    user_id='me', 
                                    msg_id=emails_in[0]['id'])
                latest_email_in_header = gmail.GetMessageHeader(latest_email_in)
                self.latest_email_in_date = gmail.ParseDate(latest_email_in_header['Date'])
            except:
                logging.warning('latest_email_in not added')
        else:
            self.total_emails_in = 0

        # Emails out fields
        if emails_out and len(emails_out) > 0:
            self.total_emails_out = len(emails_out)
            try:
                latest_email_out = gmail.GetMessage(service=service, 
                                    user_id='me', 
                                    msg_id=emails_out[0]['id'])
                latest_email_out_header = gmail.GetMessageHeader(latest_email_out)
                self.latest_email_out_date = gmail.ParseDate(latest_email_out_header['Date'])
            except:
                logging.warning('latest_email_out not added')
        else:
            self.total_emails_out = 0

        # Finished with all Connection fields
        self.last_updated = datetime.datetime.now()
        self.save()
