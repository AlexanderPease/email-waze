import settings
from mongoengine import *
import tweepy, logging

mongo_database = settings.get('mongo_database')
connect('profile', host=mongo_database['host'])

class Profile(Document):
	name = StringField(required=False)
	email = EmailField(required=True) # This will have to become a list at some point, or have a secondary email list

	# When this address was last emailed. Helps guess if an email address is still being used or not
	last_emailed = DateTimeField(required=False) 

	#emailed_by = ListField(field=DictField(), default=list) # or look at one to many with listfields
	#emailed_to = ListField(field=DictField(), default=list)

	def __str__(self):
		if self.name():
			return self.name()
		else:
			return 'No name found'



	


	


