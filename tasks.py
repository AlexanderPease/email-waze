from celery import Celery
from celery.decorators import periodic_task
from datetime import timedelta
import settings, logging

from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection

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
                        except DoesNotExist:
                            p = Profile.add_new(name=name, email=email)

                        # Ensure p was succesfully created before 
                        # adding a Connection
                        if p:
                            # Search Connection database to see if this is a new contact
                            c, created_flag = Connection.objects.get_or_create(user=u,
                                                                            profile=p)

                            # If newly created Connection, fill it in by
                            # searching Gmail API
                            if not created_flag:
                                logging.info('%s already exists, not updating')
                            else:
                                logging.info('Created %s' % c)
                                # See if any messages match query
                                emails_in = gmail.ListMessagesMatchingQuery(service=gmail_service, 
                                                                            user_id='me', 
                                                                            query= "from:" + p.email)
                                emails_out = gmail.ListMessagesMatchingQuery(service=gmail_service, 
                                                                            user_id='me', 
                                                                            query= "to:" + p.email)

                                # Emails in fields
                                if emails_in and len(emails_in) > 0:
                                    c.total_emails_in = len(emails_in)

                                    # Get dates of latest emails in and out
                                    try:
                                        latest_email_in = gmail.GetMessage(service=gmail_service, 
                                                            user_id='me', 
                                                            msg_id=emails_in[0]['id'])
                                        latest_email_in_header = gmail.GetMessageHeader(latest_email_in)
                                        c.latest_email_in_date = gmail.ParseDate(latest_email_in_header['Date'])
                                    except:
                                        logging.warning('latest_email_in not added')
                                else:
                                    c.total_emails_in = 0

                                # Emails out fields
                                if emails_out and len(emails_out) > 0:
                                    c.total_emails_out = len(emails_out)
                                    try:
                                        latest_email_out = gmail.GetMessage(service=gmail_service, 
                                                            user_id='me', 
                                                            msg_id=emails_out[0]['id'])
                                        latest_email_out_header = gmail.GetMessageHeader(latest_email_out)
                                        c.latest_email_out_date = gmail.ParseDate(latest_email_out_header['Date'])
                                    except:
                                        logging.warning('latest_email_out not added')
                                else:
                                    c.total_emails_out = 0

                                # Finished with all Connection fields
                                logging.info(c.latest_email_out_date)
                                logging.info(c.latest_email_in_date)
                                c.last_updated = datetime.datetime.now()
                                c.save()
                        else:
                            logging.warning('Profile and Connection not added')
    else:
        logging.warning('User %s could not log in to Gmail or Contacts API', user)



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