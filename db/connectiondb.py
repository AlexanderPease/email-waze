import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
import logging, datetime



mongo_database = settings.get('mongo_database')
connect('connection', host=mongo_database['host'])

class Connection(Document):
    # The User who has corresponded with... 
    user = ReferenceField(User, required=True)

    # ...the email address of this Profile
    profile = ReferenceField(Profile, required=True) 

    total_emails_in = IntField()
    total_emails_out = IntField()
    last_email_in_date = DateTimeField()
    last_email_out_date = DateTimeField()

    # Last time a job was run on User self.user to update this document
    last_updated = DateTimeField()

    # Compound index so that pair of user, profile must be unique
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

