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
		
		### Add error handling if one of these required fields can't be found
		from_address = self.get_argument('From','')
		if not from_address:
			from_address = self.get_argument('sender','')
		logging.info("From: %s" % from_address)
		
		to_address = self.get_argument('To', '')
		if not to_address:
			to_address = self.get_argument('recipient', '')
		logging.info("To: %s" % to_address)
		
		subject = self.get_argument('Subject', '')
		logging.info("Subject: %s" % subject)

		body = self.get_argument('body-html', '')
		if not body:
			body = self.get_argument('body-plain', '')
		logging.info("body %s" % body)

		date = self.get_argument('Date', '')
		logging.info("date %s" % date)
		
		try:
			to_address_string = to_address.split('@')[0] # Splits out "@ansatz.me"
			p = Profile.objects.get(email_obscured=to_address_string)
			logging.info(p)
		except:
			logging.warning('Could not find profile for obscured address: %s' % to_address)

		try:
			self.send_mail(to_address=p.email,
						from_address=from_address,
						subject=subject,
						html_text=body)
		except:
			logging.warning("Failed to send email to %s" % p.email)

		return self.set_status(200)
