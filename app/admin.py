import app.basic, ui_methods
import tornado.web
import settings
import requests, datetime, logging

from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection


###########################
### List the available admin tools
### /admin
###########################
class AdminHome(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render('admin/admin_home.html')


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
            u = User.objects
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
### Scratch for debugging
### /admin/scratch
###########################
class Scratch(app.basic.BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')

        u = User.objects.get(email="me@alexanderpease.com")
        gmail_service = u.get_service(service_type='gmail')
        messages = gmail.ListMessagesMatchingQuery(service=gmail_service,
                                                user_id='me',
                                                query='after:%s' % u.last_updated.strftime('%Y/%m/%d'))

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

        return self.render('admin/admin_home.html')
