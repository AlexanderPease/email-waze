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
		from_address = self.get_argument('sender','')
		logging.info("from %s" % from_address)
		
		to_address = self.get_argument('recipient', '')
		logging.info("recipient %s" % to_address)

		to_address = self.get_argument('To', '')
		logging.info("To: %s" % to_address)
		
		subject = self.get_argument('subject', '')
		logging.info("subject %s" % subject)

		body = self.get_argument('body', '')
		logging.info("body %s" % body)

		body_plain = self.get_argument('body-plain', '')
		logging.info("body-plain %s" % body_plain)

		date = self.get_argument('Date', '')
		logging.info("date %s" % date)
		
		logging.info(self.request.arguments)


		
		try:
			p = Profile.objects.get(email_obscured=to_address)
		except:
			logging.warning('Could not find profile for email sent to %s' % to_address)

		return self.set_status(200)
