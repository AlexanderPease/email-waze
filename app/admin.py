import app.basic
import tornado.web
import settings
import requests, datetime, logging

from db.profiledb import Profile

###########################
### List the available admin tools
### /admin
###########################
class AdminHome(app.basic.BaseHandler):
  #@tornado.web.authenticated
  def get(self):
    return self.render('admin/admin_home.html', tweets=tweets, msg=msg, err=err)


###########################
### ASCII view of database
### /admin/profile_database
###########################
class DB_Profiles(app.basic.BaseHandler):
  #@tornado.web.authenticated
  def get(self):
    #if self.current_user not in settings.get('staff'):
    #  self.redirect('/')
    #else:
    p = Profile.objects
    
    return self.render('admin/db_profiles.html', profiles=p)

