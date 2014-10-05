import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
import logging, datetime
from app import gmail
import gdata.contacts.client

mongo_database = settings.get('mongo_database')
connect('connection', host=mongo_database['host'])

class Connection(Document):
    # The User who has corresponded with... 
    user = ReferenceField(User, required=True)

    # ...the email address of this Profile
    profile = ReferenceField(Profile, required=True) 

    total_emails_in = IntField()
    total_emails_out = IntField()
    latest_email_in_date = DateTimeField()
    latest_email_out_date = DateTimeField()

    # Last time a job was run on User self.user to update this document
    last_updated = DateTimeField()

    # Compound index so that pair of self.user and self.profile must be unique
    meta = {
        'indexes': [
            {'fields': ['user', 'profile'], 'unique': True},
        ]
    }


    def __str__(self):
        return 'Connection: User %s <-> Profile %s' % (self.user, self.profile)



    @classmethod
    def test_class(cls):
        """
        Only run on development or testing database!
        """

        for c in Connection.objects():
            c.delete()

        u = User.objects.get(email='me@alexanderpease.com')

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
                            # Profile. get_or_create() was working. 

                            # Search Profile database to see if profile exists
                            try:
                                p = Profile.objects.get(email=email)
                            except DoesNotExist:
                                p = None

                            # Create new Profile document if DNE
                            if not p:
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
            logging.warning('User %s could not log in to Gmail or Contacts API', user)

        ####!!!!
        return


        # Unique compound index test
        u = User.objects.get(email='alexander@usv.com')
        p = Profile.objects.get(email='me@alexanderpease.com')

        u2 = User.objects.get(email='alexander@usv.com')
        p2 = Profile.objects.get(email='me@alexanderpease.com')

        c = Connection(user=u, profile=p)
        c2 = Connection(user=u2, profile=p2)
        c.save()

        try:
            c2.save()
            raise Exception
        except NotUniqueError:
            c.delete()
            logging.info('Passed unique compound index test')
        except:
            logging.warning('Failed unique compound index test')

        # Schema test
        u = User.objects.get(email='alexander@usv.com')
        p = Profile.objects.get(email='me@alexanderpease.com')
        try:
            c =Connection(user=u,
                    profile=p, 
                    total_emails_in=2,
                    total_emails_out=99999,
                    last_email_out_date=datetime.datetime.today(),
                    last_email_in_date=datetime.datetime.today(),
                    last_updated=datetime.datetime.today())
            c.save()
            c.delete()
            logging.info('Passed schema test')
        except:
            logging.warning('Failed schema test')

        # Volume test
        for u in User.objects(name__icontains="Alexander"):
            for p in Profile.objects(name__icontains="Alexander"):
                c =Connection(user=u,
                        profile=p, 
                        total_emails_in=2,
                        total_emails_out=99999,
                        last_email_out_date=datetime.datetime.today(),
                        last_email_in_date=datetime.datetime.today(),
                        last_updated=datetime.datetime.today())
                c.save() 
                #logging.warning('Failed volume test saving to database')
        for c in Connection.objects():
            c.delete()

