import settings
from mongoengine import *
import httplib2, logging

# Google API OAUTH2 dependencies
from oauth2client.client import OAuth2Credentials
from googleapiclient.discovery import build 
import gdata.gauth 
import gdata.contacts.client

mongo_database = settings.get('mongo_database')
connect('user', host=mongo_database['host'])

class GmailJobField(EmbeddedDocument):
    last_job = DateTimeField()
    success = BooleanField()

    # If success is True, this field is None
    # If a job failed, this saves the date of the last successful email
    # Start the next job by searching Gmail for emails newer than this date
    fail_date = DateTimeField() 


class User(Document):
    # Everything comes from Google OAuth2
    google_credentials = StringField(required=True) # Saved by OAuth2Credentials.to_json()
    google_credentials_scope = StringField(required=True) # Save OAUTH_SCOPE for each user, in case this evolves
    
    ### Track status of updates/jobs run on this user
    # Tracks when Gmail was last scraped
    gmail_job = EmbeddedDocumentField(GmailJobField)
    # Tracks when Google Contacts was last scraped
    google_contacts_job = DateTimeField() 

    email = EmailField(required=True) 
    name = StringField(required=True)

    def __str__(self):
        return self.name + ' <' + self.email + '>'

    def gmail_job_start_date(self):
        """
        Returns None if this User's Gmail account has never been scraped. 
        Or else returns what date to start the next Gmail. 
        """
        if self.gmail_job.success is True:
            if self.last_job:
                return self.last_job
            else:
                raise Exception
        elif self.gmail_job.success is False:
            if self.fail_date:
                return self.fail_date
            else:
                raise Exception
        # GmailJob() has not been run on this user yet
        else:
            return None

    def get_service(self, service_type='gmail', version='v1'):
        """
        Returns Google service object for calling APIs

        Args: 
            service_type: Default 'gmail', or use 'oauth2' or 'plus'
        """
        try:
            credentials = OAuth2Credentials.new_from_json(self.google_credentials)
            http = httplib2.Http()
            http = credentials.authorize(http)
            return build(service_type, version, http=http)
        except:
            logging.error('Could not return Google Discovery APIs service object for User "%s"' % self)
            return

    def get_gd_client(self):
        """
        Returns client for Google Data APIs. Currently returns for Contacts API only
        Uses same google_credentials as get_service() for GMail and newer Google APIs

        Args: 
            service_type: Default 'contacts'
        """
        try:
            credentials = OAuth2Credentials.new_from_json(self.google_credentials)
            auth2token = gdata.gauth.OAuth2TokenFromCredentials(credentials)
            gd_client = gdata.contacts.client.ContactsClient(source='<var>Ansatz/var>')
            gd_client = auth2token.authorize(gd_client)
            return gd_client
        except:
            logging.error('Could not return Google Data APIs client for User "%s"' % self)
            return


