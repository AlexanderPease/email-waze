import app.basic, settings, ui_methods, tornado.web
import logging
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
from connectionsets import GroupConnectionSet, ProfileConnectionSet
import connectionsets

########################
### Returns email of self
### /api/currentuseremail
########################
class CurrentUserEmail(app.basic.BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        return current_user.email




