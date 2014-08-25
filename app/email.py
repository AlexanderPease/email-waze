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
		print 'YESESESESESES'

		to_address = '????'
		try:
			p = Profile.objects.get(email_obscured=to_address)
		except:
			logging.warning('Could not find profile for email sent to %s' % to_address)
