import settings
from mongoengine import *
import tweepy, logging

mongo_database = settings.get('mongo_database')
connect('profile', host=mongo_database['host'])

class Profile(Document):
	name = StringField(required=False)
	email = StringField(required=True) # This will have to become a list at some point

	def __str__(self):
		if self.name():
			return self.name()
		else:
			return 'Profile without a name'



	


	


