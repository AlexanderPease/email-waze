import sys, os
try: 
		sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
		import settings
except:
		pass

from db.userdb import User
from app.gmail import GmailJob
import logging
logging.getLogger().setLevel(logging.INFO)

def main():
	for u in User.objects(email='falicon33@gmail.com'):
		# Run jobs on all users that are brand new
		if not u.if_gmail_job():
			logging.info("Starting GmailJob for %s" % u)
			GmailJob(u)
if __name__ == "__main__":
		main()