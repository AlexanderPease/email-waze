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
        p = Profile(name='foo', email='foo@test.com')
        logging.info(p)
        logging.info(p.burner)
        p.save()

        p2 = Profile(name='foo', email='foo2@test.com')
        logging.info(p2)
        logging.info(p2.burner)
        p2.save()

        p.delete()
        p2.delete()
        
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
