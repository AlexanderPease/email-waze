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

    def print_stats(self):
        logging.info(self)
        logging.info("Emails in: %s (%s)" % (self.total_emails_in, self.latest_email_in_date_string()))
        logging.info("Emails out: %s (%s)" % (self.total_emails_out, self.latest_email_out_date_string()))

    def latest_email_in_date_string(self):
        return date_to_string(self.latest_email_in_date)

    def latest_email_out_date_string(self):
        return date_to_string(self.latest_email_out_date)

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
            latest_email_in = gmail.GetMessage(service=service, 
                                            user_id='me', 
                                            msg_id=emails_in[0]['id'])
            if not latest_email_in:
                logging.warning('latest_email_in not added b/c gmail.GetMessage did not return message')
            else:
                try:
                    latest_email_in_header = gmail.GetMessageHeader(latest_email_in)
                except:
                    logging.warning('gmail.GetMessageHeader error')

                if 'Date' in latest_email_in_header:
                    self.latest_email_in_date = gmail.ParseDate(latest_email_in_header['Date'])
                else:
                    logging.info('Date not in email header')
        else:
            self.total_emails_in = 0

        # Emails out fields
        if emails_out and len(emails_out) > 0:
            self.total_emails_out = len(emails_out)
            latest_email_out = gmail.GetMessage(service=service, 
                                                user_id='me', 
                                                msg_id=emails_out[0]['id'])
            if not latest_email_out:
                logging.warning('latest_email_out not added b/c gmail.GetMessage did not return message')
            else:
                try:
                    latest_email_out_header = gmail.GetMessageHeader(latest_email_out)
                except:
                    logging.warning('gmail.GetMessageHeader error')

                if 'Date' in latest_email_out_header:
                    self.latest_email_out_date = gmail.ParseDate(latest_email_out_header['Date'])
                else:
                    logging.info('Date not in email header')
        else:
            self.total_emails_out = 0

        # Finished with all Connection fields
        self.last_updated = datetime.datetime.now()
        self.save()

def date_to_string(datetime_object):
        if datetime_object:
            return datetime_object.strftime('%Y/%m/%d')
        else:
            return 'N/A'
