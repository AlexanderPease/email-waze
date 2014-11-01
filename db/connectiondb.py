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

    # In is the Profile emailing the User
    total_emails_in = IntField()
    latest_email_in_date = DateTimeField()


    # Out is the User emailing the Profile
    total_emails_out = IntField()
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

    # Not used yet
    def to_json(self):
        json = {'connected_user_name': self.user.name,
            'connected_user_email': self.user.email,
            'connected_profile_name': self.profile.name,
            'connected_profile_email': self.profile.email,
            'total_emails_in': self.total_emails_in, 
            'latest_email_in_date': self.latest_email_in_date_string(),
            'total_emails_out': self.total_emails_out,
            'latest_email_out_date': self.latest_email_out_date_string()}
        return json

    def latest_email_in_date_string(self):
        if self.latest_email_in_date:
            return self.latest_email_in_date.strftime('%Y/%m/%d')
        elif self.total_emails_in:
            return 'Not found'
        else:
            return 'N/A'

    def latest_email_out_date_string(self):
        if self.latest_email_out_date:
            return self.latest_email_out_date.strftime('%Y/%m/%d')
        elif self.total_emails_out:
            return 'Not found'
        else:
            return 'N/A'

    def days_since_emailed_out(self):
        ''' 
        Returns how many days since the User has emailed the Profile,
        i.e. # days since self.latest_email_out_date
        '''
        if self.latest_email_out_date:
            delta = datetime.datetime.today() - self.latest_email_out_date
            if delta.days > 0:
                return delta.days
            else:
                return 'Today'
        else:
            return None

    def days_since_emailed_in(self):
        ''' 
        Returns how many days since the Profile has emailed the User,
        i.e. # days since self.latest_email_in_date
        '''
        if self.latest_email_in_date:
            delta = datetime.datetime.today() - self.latest_email_in_date
            if delta.days > 0:
                return delta.days
            else:
                return 'Today'
        else:
            return None

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
        elif not self.total_emails_in:
            # Only set to 0 if no prior total_emails_in. 
            # Occasionally Gmail won't return anything, so this way we keep the last
            # total_emails_in without resetting to zero
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
        elif not self.total_emails_out:
            # Only set to 0 if no prior total_emails_out. 
            # Occasionally Gmail won't return anything, so this way we keep the last
            # total_emails_out without resetting to zero
            self.total_emails_out = 0

        # Finished with all Connection fields
        self.last_updated = datetime.datetime.now()
        self.save()


    def print_stats(self):
        """
        For debugging
        """
        logging.info(self)
        logging.info("Emails in: %s (%s)" % (self.total_emails_in, self.latest_email_in_date_string()))
        logging.info("Emails out: %s (%s)" % (self.total_emails_out, self.latest_email_out_date_string()))




