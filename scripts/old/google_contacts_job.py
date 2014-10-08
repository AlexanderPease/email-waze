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


def new_users():
    """
    Runs ContactsJob on users that have never had ContactsJob run on them before
    """
    for u in User.objects():
        if not u.google_contacts_job:
            logging.info("Running ContactsJob for User %s" % u)
            success_flag = ContactsJob(u)
            if success_flag:
                u.google_contacts_job = datetime.datetime.now()
                u.save()

def all_users():
    """
    Runs ContactsJob on all users
    """
    for u in User.objects():
        logging.info("Running ContactsJob for User %s" % u)
        success_flag = ContactsJob(u)
        if success_flag:
            u.google_contacts_job = datetime.datetime.now()
            u.save()

def main():
    new_users()


if __name__ == "__main__":
        main()