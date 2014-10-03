import app.basic, settings, ui_methods
import logging
import tornado.web
from db.userdb import User


########################
### Settings page for a user
### /user/(?P<username>[A-z-+0-9]+)/settings/?
########################
class UserSettings(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, username=None):
        if username is None and self.current_user:
            username = self.current_user
        if username != self.current_user:
            raise tornado.web.HTTPError(401)

        # Find user by email
        user = User.objects.get(email=username)
        if not user:
            raise tornado.web.HTTPError(404)

        msg = self.get_argument("msg", None)
        
        self.render('user/settings.html', user=user)






