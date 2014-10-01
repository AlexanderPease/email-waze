import app.basic
import tornado.web
import settings
import requests, datetime, logging

from db.profiledb import Profile
from db.userdb import User

###########################
### List the available admin tools
### /admin
###########################
class AdminHome(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):

        profiles = Profile.objects.distinct("burner")
        print len(profiles)
        profiles = Profile.objects
        print len(profiles)
        Profile.ensure_index("burner")

        #profiles = Profile.objects()
        #for p in profiles:
        #    p.set_burner_by_algo()

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
