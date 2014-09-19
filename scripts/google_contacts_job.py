import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
    import settings
except:
    pass

from db.userdb import User
from app.google_contacts import ContactsJob
import logging, datetime
logging.getLogger().setLevel(logging.INFO)

def main():
    for u in User.objects():
        # Only on those that haven't had job run yet
        if not u.google_contacts_job:
            logging.info("Running ContactsJob for User %s" % u)
            success_flag = ContactsJob(u)
            if success_flag:
                u.google_contacts_job = datetime.datetime.now()
                u.save()


if __name__ == "__main__":
        main()