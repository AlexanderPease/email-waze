import settings
from mongoengine import *
import httplib2, logging
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials

mongo_database = settings.get('mongo_database')
connect('user', host=mongo_database['host'])

class User(Document):
	# Everything comes from Google OAuth2
	google_credentials = StringField(required=True) # Saved by OAuth2Credentials.to_json()
	google_credentials_scope = StringField(required=True) # Save OAUTH_SCOPE for each user, in case this evolves
	gmail_job = DictField() # Tracks when Gmail was last scraped
	email = EmailField(required=True) 
	name = StringField(required=True)

	def __str__(self):
		return self.name + ' <' + self.email + '>'

	def if_gmail_job(self):
		"""
		Returns if this User's Gmail has been scraped AT ALL
		"""
		if 'last_job' in self.gmail_job.keys():
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
			logging.error('Could not return Google service object for return User %s' % self)
			return

	    
	
		


		


