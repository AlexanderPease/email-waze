import app.basic, ui_methods
import tornado.web
import settings
import requests, datetime, logging

from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection

from tests.test_group import test_group_class

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
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')

        """
        zander = 
        g = Group(name="All", users = [users[0]])
        for u in users:
            g.add_user(u)
        g.save()
        """

        #test_group_class()

        return self.render('admin/admin_home.html')
