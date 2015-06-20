
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
from db.gmailmessagejobdb import GmailMessageJob
from db.gmailjobdb import GmailJob
from db.taskdb import Task
import tasks
from methods import send_email, send_email_template


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
### ASCII view of database
### /admin/db_tasks
###########################
class DB_Tasks(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user not in settings.get('staff'):
            self.redirect('/')
        else:
            t = Task.objects()
            return self.render('admin/db_tasks.html', tasks=t)



###########################
### Google Webmaster Verification
### /google077100c16d33120b
###########################
class GoogleWebmaster(app.basic.BaseHandler):
    def get(self):
        return self.render('admin/google077100c16d33120b.html')


