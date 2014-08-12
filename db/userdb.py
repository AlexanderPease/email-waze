import settings
from mongoengine import *
import logging

mongo_database = settings.get('mongo_database')
connect('user', host=mongo_database['host'])

class User(Document):
	# Everything comes from Google OAuth2
	google_credentials = StringField(required=True) # Saved by OAuth2Credentials.to_json()
	email = EmailField(required=True) 
	name = StringField(required=True)

	#def __str__(self):
	#	return self.name + ' <' + self.email + '>'

	'''
	def email(self):
		return self.email

	
	def name(self):
		if self.name:
			return self.name
		else:
			return '<Empty Field>'
	'''

	def google_oauth2_credentials(self):
		""" Returns instance of OAuth2Credentials """ 
		try:
			return self.google_credentials.from_json()
		except:
			logging.warning("Could not return Google OAuth2 Credentials")
			return None

	"""
	def get_service(self):
		credentials = self.google_oauth2_credentials()
		http = httplib2.Http()
	    http = credentials.authorize(http)
	    service = build('gmail', 'v1', http=http)
	    user_info = service.people().get(userId='me').execute()
	"""
		


		


