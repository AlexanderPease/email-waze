import sys, os
try: 
	sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
	import settings
except:
	pass

from db.userdb import User
from db.profiledb import Profile
from db.connectiondb import Connection
import logging, datetime
logging.getLogger().setLevel(logging.INFO)


def main():
	for p in Profile.objects():
		p.save()
	'''
	for u in User.objects():
		u.save()
	'''


if __name__ == "__main__":
		main()