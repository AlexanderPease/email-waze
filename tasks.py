from celery import Celery
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from datetime import timedelta
import settings, logging, datetime
from email.utils import parseaddr
from mongoengine import DoesNotExist

from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
from db.groupdb import Group
from db.statsdb import Stats
from db.companydb import Company

import gdata.contacts.client
import app.gmail as gmail

import json

app = Celery('tasks', 
    broker=settings.get('rabbitmq_bigwig_url'),
    backend='amqp')


@periodic_task(run_every=timedelta(minutes=5))
def awake():
    """
    Keeps the worker awake 24/7
    """
    foo = 1 + 1
    logging.info('Awake!')

@periodic_task(run_every=timedelta(hours=24))
def add_stats():
    """
    Add a new entry to statsdb every 24 hours
    """
    stats = Stats(date=datetime.datetime.now())
    stats.profiles = len(Profile.objects)
    stats.users = len(User.objects)
    stats.connections = len(Connection.objects)
    stats.groups = len(Group.objects)
    stats.companies = len(Company.objects)
    stats.save()


#@periodic_task(run_every=timedelta(hours=24))
def company_list():
    """
    Update company list JSON doc for typeahead service
    """
    with open('static/json/company_list.json', 'w') as f:
        json_list = []
        for c in Company.objects():
            name = c.get_name()
            if name and "N/A" not in name:
                c_json = {
                "name": name,
                "id": str(c.id),
                "domain": c.domain
                }
                if 'logo' in c.clearbit.keys():
                    c_json['logo'] = c.clearbit['logo']
                else:
                    c_json['logo'] = None
                json_list.append(c_json)
        json.dump(json_list, f)


@app.task
def onboard_user(u):
    """
    Onboards a new user by
    1. Searches through Google Contacts and creates new Profile objects if that
        email address does not yet exist in global database. 
    2. Creating Connection objects for all Profiles this User is 
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
                        update_profile_and_connection(email=email, 
                                                        name=name,
                                                        user = u,
                                                        gmail_service=gmail_service)
        u.last_updated = datetime.datetime.now()
        u.onboarded = True
        u.save()
    else:
        logging.warning('User %s could not log in to Gmail or Contacts API', u)
        logging.warning(gd_client)
        logging.warning(gmail_service)


@app.task
def update_user(u):
    """
    Updates Connections of a user and creates any new Profiles as needed.
    Uses User field last_updated to filter emails to run through.

    Args:
        u is an existing User to the app. If u is a new User this function will
        take a long time. 
    """
    logging.info("Updating %s in tasks.update_user()" % u)
    gmail_service = u.get_service(service_type='gmail')
    if not gmail_service:
        logging.info("Could not instantiate authenticated service for %s" % u)
        return
    messages = gmail.ListMessagesMatchingQuery(service=gmail_service,
                                                user_id='me',
                                                query='after:%s' % u.last_updated.strftime('%Y/%m/%d'))
    if not messages:
        return

    # Track list of emails that have been updated by this function
    updated_emails = []
    msg_counter = 0
    total_num = len(messages)
    for msg_info in messages:
        logging.info("Checking message of id: %s (%s of %s total)" % (msg_info['id'], msg_counter, total_num))
        msg = gmail.GetMessage(gmail_service, 'me', msg_info['id'])
        if msg:
            msg_header = gmail.GetMessageHeader(msg)
            if msg_header:
                header_list = ['Delivered-To', 'Return-Path', 'From', 'To'] # Which email addresses to check
                for header in header_list:
                    if header in msg_header.keys():
                        field = parseaddr(msg_header[header]) # Allows local emails addresses unfortunately
                        name = field[0]
                        email = field[1]

                        # Only consider email if it hasn't yet been done 
                        # for this user 
                        if email not in updated_emails:
                            updated_emails.append(email)
                            if name and name is not "" and email and email is not "":
                                logging.info("Good pair: %s <%s>" % (name, email))
                                update_profile_and_connection(email=email,
                                                            name=name,
                                                            user=u,
                                                            gmail_service=gmail_service)
        msg_counter = msg_counter + 1

    # Save completed job specs to user
    u.last_updated = datetime.datetime.now()
    u.save()
    logging.info("Finished updating %s in tasks.update_user()" % u)
    return


@periodic_task(run_every=timedelta(hours=12))
def update_users():
    """
    Update all users every 24 hours
    """
    for u in User.objects:
        try:
            update_user(u)
        except:
            pass


def update_profile_and_connection(email, name, user, gmail_service):
    """
    Logic to update both Profile and Connection databases for the given 
    User and an email and name
    """ 
    # The following lines could be condensed if 
    # Profile.get_or_create() was working. 
    try:
        p = Profile.objects.get(email_lower=email.lower())
        logging.info("Found existing Profile %s" % p)
    except DoesNotExist:
        p = Profile.add_new(name=name, email=email)
        logging.info(p)

    # Ensure p was succesfully created before 
    # adding a Connection. Profile.add_new() sometimes fails (for good reason,
    # like email address was a reply.craigslist.com one)
    if not p:
        logging.warning("Could not find or add Profile of email %s" % email)
        return

    # Create connection if not to oneself
    if user.email == p.email:
        logging.info('Connection not created for email address %s to itself' % user.email)
    else:
        # Search Connection database to see if this is a new contact
        c, created_flag = Connection.objects.get_or_create(user=user,
                                                        profile=p)
        # If newly created Connection, fill it in by
        # searching Gmail API
        if created_flag:
            logging.info('Created %s' % c)
        else:
            logging.info('%s already exists, not updating' % c)

        # Updates fields of c by searching through users'
        # entire Gmail inbox 
        c.populate_from_gmail(service=gmail_service)

### Local 
logging.getLogger().setLevel(logging.INFO)
def remove_capitalization_redundant_pc():
    count = 1;
    for p in Profile.objects():
        logging.info('Count: %s' % count)
        ps = Profile.objects(email__iexact=p.email)
        if len(ps) > 1:
            merge_profiles(ps)
        count += 1

def merge_profiles(ps):
    if len(ps) != 2:
        logging.warning('%s profiles given' % len(ps)) 
    else:
        p1 = ps[0]
        p2 = ps[1]
        # Just iterate through p2 Connections
        cs2 = Connection.objects(profile=p2)
        for c2 in cs2:
            u = c2.user
            # See if there is a conflicting Connection
            try:
                c1 = Connection.objects.get(profile=p1, user=u)
            except:
                c1 = None
            if c1:
                # Reconcile c and c_dup
                c1.total_emails_out += c2.total_emails_out
                c1.total_emails_in += c2.total_emails_in
                if c1.days_since_emailed_out() > c2.days_since_emailed_out():
                    c1.latest_email_out_date = c2.latest_email_out_date
                if c1.days_since_emailed_in() > c2.days_since_emailed_in():
                    c1.latest_email_in_date = c2.latest_email_in_date
                c2.delete()
            else:
                # No conflict, attach c to p1
                c2.profile = p1
                c2.save()
        p2.delete()

def print_info(email):
    ps = Profile.objects(email__iexact=email)
    for p in ps:
        logging.info('------------')
        logging.info(p)
        cs = Connection.objects(profile=p)
        logging.info(cs)
        logging.info('------------')


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