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
		logging.info('Parsing email from Mailgun API...')
		sender = self.get_argument('sender','no sender')
		logging.info(sender)
		subject = self.get_argument('subject', 'no subject')
		logging.info(subject)
		to_address = self.get_argument('to', 'no to')
		logging.info(to_address)
		logging.info(self.request)


		
		try:
			p = Profile.objects.get(email_obscured=to_address)
		except:
			logging.warning('Could not find profile for email sent to %s' % to_address)

		return self.set_status(200)
