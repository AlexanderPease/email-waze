import app.basic, settings, ui_methods
import logging
import tornado.web
from mongoengine.queryset import Q
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

        # Display User's Groups
        groups = user.get_groups()
        group_invites_raw = Group.objects(Q(invited_emails=self.current_user) | Q(domain_restriction__icontains=user.get_domain()))
        group_invites = []
        for g in group_invites_raw:
            if g not in groups:
                group_invites.append(g)


        # Display User's ansatz email
        try:
            profile = Profile.objects.get(email=user.email)
        except: 
            profile = None

        # Possible message or error
        msg = self.get_argument('msg', '')
        err = self.get_argument('err', '')

        return self.render('user/user_settings.html', user=user, 
                                                    groups=groups, 
                                                    group_invites=group_invites,
                                                    profile=profile, 
                                                    msg=msg, 
                                                    err=err)





