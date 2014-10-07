import app.basic, settings, ui_methods
import logging
import tornado.web
from db.userdb import User


########################
### Settings page for a user
### /user/settings
########################
class UserSettings(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Find user by email
        user = User.objects.get(email=self.current_user)
        if not user:
            raise tornado.web.HTTPError(404)

        #msg = self.get_argument("msg", None)
        return self.render('user/settings.html', user=user)





