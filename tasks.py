from celery import Celery
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from datetime import timedelta
import settings, logging, datetime
from mongoengine import DoesNotExist

from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection

import gdata.contacts.client

#from app.gmail import GmailJob
#from scripts.google_contacts_job import main as google_contacts_job

app = Celery('tasks', 
    broker=settings.get('rabbitmq_bigwig_url'),
    backend='amqp')

@app.task
def add(x, y):
    return x + y


@app.task
def onboard_user(u):
    """
    Onboards a new user by
    1. Searches through Google Contacts and creates new Profile objects if that
        email address does not yet exist in global database. 
    2. Creating Correspondence objecst for all Profiles this User is 
        connected to

    Args:
        u is a new User to the app. 
    """
    logging.info('Onboarding new user %s' % u)

    # Get Contacts and Gmail access for user
    gd_client= u.get_gd_client()
    gmail_service = u.get_service(service_type='gmail')

    if gd_client and gmail_service:
        query = gdata.contacts.client.ContactsQuery()
        # GetContacts defaults to return 25 contacts, so extend query first
        query.max_results = 99999 

        try: 
            feed = gd_client.GetContacts(q=query)
        except:
            logging.warning('User %s does not have Google Contacts API permission' % user)
            return

        # Add all email addresses from feed on best effort basis
        for i, entry in enumerate(feed.entry):
            # Get name, if it's in the entry
            try:
                name = entry.name.full_name.text
            except:
                name = None

            # Contact must have a name to be added to database
            if name:
                for email in entry.email:
                    if email.primary and email.primary == 'true' and email.address:
                        # Entry has passed tests and will now be added to database
                        email = email.address
                        logging.info('Adding: %s <%s>' % (name, email))

                        # The following lines could be condensed if 
                        # Profile.get_or_create() was working. 
                        try:
                            p = Profile.objects.get(email=email)
                            logging.info(p)
                        except DoesNotExist:
                            p = Profile.add_new(name=name, email=email)
                            logging.info(p)
                        logging.info('above line should show profile')

                        # Ensure p was succesfully created before 
                        # adding a Connection. Profile.add_new() sometimes fails
                        if p:
                            # Search Connection database to see if this is a new contact
                            c, created_flag = Connection.objects.get_or_create(user=u,
                                                                            profile=p)
                            # If newly created Connection, fill it in by
                            # searching Gmail API
                            if not created_flag:
                                logging.info('%s already exists, not updating' % c)
                            else:
                                logging.info('Created %s' % c)

                                # Updates fields of c by searching through users'
                                # entire Gmail inbox 
                                c.populate_from_gmail(service=gmail_service)
                        else:
                            logging.warning('Profile and Connection not added')
    else:
        logging.warning('User %s could not log in to Gmail or Contacts API', user)

@periodic_task(run_every=timedelta(hours=24))
def update_users():
    """
    Update users 
    """
    pass

"""
@periodic_task(run_every=timedelta(hours=24))
def run_google_contacts_job():
    logging.info("Celery worker starting tasks.run_google_contacts_job()")
    google_contacts_job()
    logging.info("Celery worker finished tasks.run_google_contacts_job()")
"""
"""
@app.task
def run_gmail_job():
    logging.info("Celery worker starting tasks.run_gmail_job()")

    # Run jobs on all users that are brand new first...
    for u in User.objects():
        if not u.gmail_job.success:
            logging.info("Starting GmailJob for new User %s" % u)
            GmailJob(u)

    # ...then updates existing users
    for u in User.objects():
        logging.info("Starting GmailJob for existing User %s" % u)
        GmailJob(u)

    logging.info("Celery worker finished tasks.run_gmail_job()")
"""