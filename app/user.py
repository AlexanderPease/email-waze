import app.basic, settings, ui_methods
import logging
import tornado.web
from mongoengine.queryset import Q, DoesNotExist, MultipleObjectsReturned
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
        try:
            user = User.objects.get(email=self.current_user)
        except MultipleObjectsReturned:
            raise tornado.web.HTTPError(500)
        except DoesNotExist:
            raise tornado.web.HTTPError(404)

        # Display User's Groups
        groups = user.get_groups()
        group_invites_raw = Group.objects(Q(invited_emails=self.current_user) | Q(domain_setting__icontains=user.get_domain()))
        group_invites = []
        for g in group_invites_raw:
            if g not in groups:
                group_invites.append(g)

        # User pays for groups larger than 5 people
        paying_groups_raw = groups(admin=user)
        paying_groups = []
        for g in paying_groups_raw:
            if len(g.users) > 5:
                paying_groups.append(g)

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
            paying_groups=paying_groups,
            profile=profile, 
            msg=msg, 
            err=err,
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)


########################
### Welcome page for a new user
### /user/welcome
########################
class UserWelcome(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Find user by email
        try:
            user = User.objects.get(email=self.current_user)
        except MultipleObjectsReturned:
            raise tornado.web.HTTPError(500)
        except DoesNotExist:
            raise tornado.web.HTTPError(404)

        if user.welcomed:
            return self.redirect('/')
        else:
            user.welcomed = True
            user.save()

        # Display User's Group invites
        # This block exists because some preexisting users may be new to onboarding
        groups = user.get_groups()
        group_invites_raw = Group.objects(Q(invited_emails=self.current_user) | Q(domain_setting__icontains=user.get_domain()))
        group_invites = []
        for g in group_invites_raw:
            if g not in groups:
                group_invites.append(g)

        return self.render('user/user_welcome.html', user=user, 
            group_invites=group_invites)







