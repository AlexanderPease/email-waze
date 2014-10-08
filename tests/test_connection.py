import settings, logging
from db.groupdb import Group
from db.userdb import User
from db.connectiondb import Connection

def test_connection_class():
    """
        Only run on development or testing database!
        """

        for c in Connection.objects():
            c.delete()

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
        for c in Connection.objects():
            c.delete()
