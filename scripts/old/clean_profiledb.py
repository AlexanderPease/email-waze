import sys, os
try: 
		sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
		import settings
except:
		pass

from db.profiledb import Profile
import logging
logging.getLogger().setLevel(logging.INFO)

def main():
	for p in Profile.objects():
		delete = False
		if 'reply' in p.email:
			delete = True
		elif 'info' in p.get_domain: # info@aminafigarova is pretty common
			delete = True
		elif  len(p.email) > 40: 
			delete = True

		if delete is True:
			logging.info('Deleted %s' % p.email)
			p.delete()


if __name__ == "__main__":
		main()
