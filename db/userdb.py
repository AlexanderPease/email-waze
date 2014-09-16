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
	fail_date = DateTimeField() # if success is True, this field is None


class User(Document):
	# Everything comes from Google OAuth2
	google_credentials = StringField(required=True) # Saved by OAuth2Credentials.to_json()
	google_credentials_scope = StringField(required=True) # Save OAUTH_SCOPE for each user, in case this evolves
	
	# Track status of updates run on this user
	gmail_job = EmbeddedDocumentField(GmailJobField)# Tracks when Gmail was last scraped
	google_contacts_job = DateTimeField() # Tracks when Contacts were last scraped

	email = EmailField(required=True) 
	name = StringField(required=True)

	def __str__(self):
		return self.name + ' <' + self.email + '>'

	def if_gmail_job(self):
		"""
		Returns if this User's Gmail has been scraped AT ALL
		"""
		if self.gmail_job.last_job:
			return True
		else:
			return False


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

	    
	
		


		


