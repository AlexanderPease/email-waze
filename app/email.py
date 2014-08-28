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
		
		try:
			to_address_string = to_address.split('@')[0] # Splits out "@ansatz.me"
			p = Profile.objects.get(email_obscured=to_address_string)
			logging.info("Found profile for %s " % p)
		except:
			logging.warning('Could not find profile for obscured address: %s' % to_address)
			return self.set_status(406) # Mailgun knows it failed but won't retry

		try:
			reply_to = from_address # User who sent the email is now the reply-to address
			from_address = 'Ansatz.me <postmaster@ansatz.me>'
			to_address = 'me@alexanderpease.com'

			self.send_mail(from_address=from_address,
						to_address=p.email,
						subject=subject,
						html_text=body)
			logging.info('Sent email from %s to obscured %s' % (from_address, p.email))
		except:
			logging.warning("Failed to send email below:")
			logging.warning("To: %s" % to_address)
			logging.warning("From: %s" % from_address)
			logging.warning("Reply-To: %s" % reply_to)
			logging.warning("Subject: %s" % subject)
			logging.warning("Date: %s" % date)
			return self.set_status(406) # Mailgun knows it failed but won't retry

		return self.set_status(200)
