import app.basic, settings, ui_methods
import logging
import tornado.web
from db.userdb import User
from db.groupdb import Group
from db.profiledb import Profile


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

        groups = user.get_groups()
        group_invites = Group.objects(invited_emails=self.current_user)

        try:
            profile = Profile.objects.get(email=user.email)
        except: 
            profile = None

        return self.render('user/user_settings.html', user=user, 
                                                    groups=groups, 
                                                    group_invites=group_invites,
                                                    profile=profile)





