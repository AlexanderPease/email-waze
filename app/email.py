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
		to_address = self.get_argument('To', '') ### Can't handle multiple email addresses?
		if not to_address:
			to_address = self.get_argument('recipient', '')
		subject = self.get_argument('Subject', '')
		body = self.get_argument('body-html', '')
		if not body:
			body = self.get_argument('body-plain', '')
		date = self.get_argument('Date', '')

		logging.info("To: %s" % to_address)
		logging.info("From: %s" % from_address)
		logging.info("Subject: %s" % subject)
		logging.info("Body: %s" % body)
		logging.info("Date: %s" % date)
		
		try:
			to_address_string = to_address.split('@')[0] # Splits out "@ansatz.me"
			p = Profile.objects.get(email_obscured=to_address_string)
			logging.info("Found profile for %s " % p)
		except:
			logging.warning('Could not find profile for obscured address: %s' % to_address)
			return self.set_status(406) # Mailgun knows it failed but won't retry

		try:
			logging.info('going into sending email')
			self.send_mail(from_address=from_address,
						to_address=p.email,
						subject=subject,
						html_text=body)
		except:
			logging.warning("Failed to send email to %s" % p.email)

		return self.set_status(200)
