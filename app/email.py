import app.basic, settings
import logging
from db.profiledb import Profile

########################
### email/forward
########################
class Forward(app.basic.BaseHandler):
	"""
	Forwards email that was sent to an obscured address to the real owner
	Sent to this webhook by Mailgun API
	"""
	def post(self):
		print 'received email'
		sender = self.get_argument('sender','fialed')
		print sender
		subject = self.get_argument('subject', 'falalal')
		print subject
		print 'sender and subject above'
		to_address = self.get_argument('to', 'falalal22')


		
		try:
			p = Profile.objects.get(email_obscured=to_address)
		except:
			logging.warning('Could not find profile for email sent to %s' % to_address)

		return self.set_status(200)
