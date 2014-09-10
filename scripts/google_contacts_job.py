import sys, os
try: 
	sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
	import settings
except:
	pass

from db.userdb import User
from app.google_contacts import ContactsJob
import logging
logging.getLogger().setLevel(logging.INFO)

def main():
	ContactsJob(User.objects.get(email="alexander@usv.com"))
	return


	for u in User.objects():
		# Run jobs on all users that are brand new
		if not u.if_gmail_job():
			ContactsJob(u)
if __name__ == "__main__":
		main()