import settings
from mongoengine import *
import logging, random
from email.utils import parseaddr

mongo_database = settings.get('mongo_database')
connect('profile', host=mongo_database['host'])

class Profile(Document):
	name = StringField(required=True) # I can relax this later
	email = EmailField(required=True, unique=True) # This will have to become a list at some point, or have a secondary email list
	email_obscured = StringField() # Obscured self.email by generating random string. This is just string doesn't include our domain. 

	# When this address was last emailed. Helps guess if an email address is still being used or not
	#last_emailed = DateTimeField()
	clicks = IntField() # How many times this link was clicked

	# Other possible names for this email address
	other_names = ListField(field=StringField(), default=list)

	# Graph fields, for future use
	#emailed_by = ListField(field=DictField(), default=list) # or look at one to many with listfields
	#emailed_to = ListField(field=DictField(), default=list)

	def __str__(self):
		return self.name + ' <' + self.email + '>'

	''' Not yet being used
	def increment_clicks(self):
		"""
		Increment whenever someone clicks on this Profile's link
		"""
		self.clicks = self.clicks + 1
		self.save()
	'''

	""" TODO: Write rules to ignore certain emails """
	@classmethod
	def add_from_gmail_message_header(cls, msg_header):
		"""
		Takes a message header from GetMessageHeader() and 
		adds to/creates entries in Profile database if necessary

		Args:
			msg_header: A message header dict returned by GetMessageHeader(). 
		""" 
		header_list = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc'] # Also Date
		for header in header_list:
			if header in msg_header.keys():
				field = parseaddr(msg_header[header]) # Allows local emails addresses unfortunately
				logging.debug(field)
				name = field[0]
				email = field[1].lower() 
				if name and email: # Only add if both are available 
					try:
						p, created = Profile.objects.get_or_create(email=email, email_obscured='%030x' % random.randrange(16**30))

						# Primary number, or save in other names?
						if p.name and name not in p.other_names:
							p.other_names = p.other_names.extend(name)
						elif not p.name:
							p.name = name
						else:
							logging.warning("No name added")
							p.delete()
							raise Exception
						p.save()

						if created:
							logging.info('Added to database: %s %s' % (p.name, p.email))
					except:
						logging.warning("Couldn't add email address: %s %s" % (name, email))


			else:
				logging.debug('No %s field in header (output in line below)' % header)
				logging.debug(msg_header)


		


		


