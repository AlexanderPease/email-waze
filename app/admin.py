
import app.basic, ui_methods
import tornado.web
import settings
import requests, datetime, logging

from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from db.statsdb import Stats
from db.companydb import Company
from db.reminderdb import ProfileReminder, CompanyReminder


###########################
### List the available admin tools
### /admin
###########################
class AdminHome(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        recent_stats = Stats.objects.order_by("-date")[0]
        return self.render('admin/admin_home.html', stats=recent_stats)


###########################
### ASCII view of database
### /admin/db_profiles
###########################
class DB_Profiles(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            p = Profile.objects
            return self.render('admin/db_profiles.html', profiles=p)


###########################
### ASCII view of database
### /admin/db_profiles
###########################
class DB_Users(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            u = User.objects.order_by("joined")
            return self.render('admin/db_users.html', users=u)


###########################
### ASCII view of database
### /admin/db_connections
###########################
class DB_Connections(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            c = Connection.objects
            return self.render('admin/db_connections.html', connections=c, encode=ui_methods.encode)

###########################
### ASCII view of database
### /admin/db_groups
###########################
class DB_Groups(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            g = Group.objects
            return self.render('admin/db_groups.html', groups=g, encode=ui_methods.encode)

###########################
### ASCII view of database
### /admin/db_companies
###########################
class DB_Companies(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            c = Company.objects()
            return self.render('admin/db_companies.html', companies=c, encode=ui_methods.encode)


###########################
### Google Webmaster Verification
### /google077100c16d33120b
###########################
class GoogleWebmaster(app.basic.BaseHandler):
    def get(self):
        return self.render('admin/google077100c16d33120b.html')

###########################
### Scratch for debugging
### /admin/scratch
###########################
class Scratch(app.basic.BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            return self.redirect('/')


        logging.info(self.user.recent_contacts())




        '''
        for pr in ProfileReminder.objects():
            logging.info(pr)
            pr.save()
            logging.info(pr.company)
        '''

        # Counts number of profiles that have an email address
        # that is duplicated (via capitalization) in the database
        '''
        num_wrong = 0
        total_len = len(Profile.objects())
        current_num = 1
        for p in Profile.objects():
            logging.info('%s/%s' % (current_num, total_len))
            current_num += 1

            ps = Profile.objects(email__contains=p.email)
            if len(ps) > 1:
                for d in ps:
                    logging.info(d)
                num_wrong += 1
        logging.info('Num emails duplicated: %s' % num_wrong)
        

        # Counts number of profiles that have an email address
        # this is not all undercase
        num_wrong = 0
        for p in Profile.objects():
            if not p.email.islower():
                num_wrong += 1
                logging.info(p.email)
        logging.info('Num emails not all undercase: %s' % num_wrong)
        '''

        # Prints out how many companies have queried Clearbit
        '''
        total = len(Company.objects())
        todo = len(Company.objects(__raw__={'date_queried_clearbit': {'$exists': True}}))
        logging.info("%s/%s" % (todo, total))
        '''

        # Update all Company docs if needed
        '''
        current_num = 1
        companies = Company.objects(__raw__={'date_queried_clearbit': {'$exists': False}})
        num_total = len(companies)
        for c in companies:
            logging.info("%s, %s/%s" % (c, current_num, num_total))
            if c.domain != "intuit.com":
                c.update_clearbit()
            current_num += 1
        '''

        # Script to check how many Company documents from clearbit have a name field
        '''
        num_name = 0
        num_clearbit = 0
        num_queried_clearbit = 0
        for c in Company.objects():
            if c.date_queried_clearbit:
                num_queried_clearbit += 1
            if c.clearbit:
                num_clearbit += 1
                if c.clearbit['name']:
                    num_name += 1
        logging.info("Name/Queried/Total: %s/%s/%s" %(num_name, num_queried_clearbit, num_clearbit))
        '''

        # Count number of distinct domains in all Profile email addresses
        '''
        profiles = Profile.objects
        domains = []
        num_profiles = len(profiles)
        counter = 1
        for p in profiles:
            logging.info(str(counter) + " / " + str(num_profiles))
            domain = p.get_domain()
            if domain not in domains:
                domains.append(domain)
            counter = counter + 1
        logging.info(domains)
        logging.info(str(len(domains)) + " distinct domains in database")
        '''

        """
        # Checks flow for getting all user credentials, refreshing if necessary
        # and executing Gmail API calls
        import gmail
        for u in User.objects:
            logging.info(u)
            gmail_service = u.get_service(service_type='gmail')
            if not gmail_service:
                logging.info("Could not create authenticated service for %s" % u)
            else:
                messages = gmail.ListMessagesMatchingQuery(service=gmail_service,
                                                user_id='me',
                                                query='after:%s' % datetime.datetime.today().strftime('%Y/%m/%d'))
                logging.info(messages)
            logging.info("---------------------")
            logging.info("")
        """

        """
        ### Delete all connections to oneself
        users = User.objects
        for u in users:
            try:
                p = Profile.objects.get(email=u.email)
                c = Connection.objects.get(profile=p, user=u)
                logging.info(c)
            except:
                pass
        """

        """
        u = User.objects.get(email="alexander@usv.com")
        p = Profile.objects.get(email="Brittany@usv.com")
        c = Connection.objects.get(user=u, profile=p)
        c.print_stats()

        service = u.get_service()
        c.populate_from_gmail(service)
        c.print_stats()
        """

        """
        p = Profile.objects
        logging.info(p)
        p = p[0]
        print p
        """

        """
        zander = 
        g = Group(name="All", users = [users[0]])
        for u in users:
            g.add_user(u)
        g.save()
        """


        #import tasks
        #tasks.onboard_user(User.objects.get(email="me@alexanderpease.com"))
        
        """
        import sys
        sys.path.append("..")
        from tests import test_both_jobs
        test_both_jobs.test_update_user()

        #from tests.test_group import test_group_class
        #test_group_class()
        """

        return self.api_response(data={})
