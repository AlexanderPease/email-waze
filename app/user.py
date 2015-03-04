import app.basic, settings, ui_methods
import simplejson as json
import logging
import tornado.web
from mongoengine.queryset import Q, DoesNotExist, MultipleObjectsReturned
from db.userdb import User
from db.groupdb import Group
from db.profiledb import Profile
from group_api import AcceptInvite


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

        # Possible message or error
        msg = self.get_argument('msg', '')
        err = self.get_argument('err', '')

        return self.render('user/user_settings.html', user=user, 
            groups=groups, 
            group_invites=group_invites,
            paying_groups=paying_groups,
            msg=msg, 
            err=err,
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string,
            nav_select='settings',
            nav_title='Settings for %s' % user.casual_name())


########################
### Welcome page for a new user
### /user/welcome
########################
class UserWelcome(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        '''
        user_welcome.html sends AJAX requests to group_api.py for user to 
        join groups he/she is invited to
        '''
        if self.user.welcomed and self.user.email not in settings.get('staff'):
            return self.redirect('/')
        else:
            self.user.welcomed = True
            self.user.save()

        # Invited Groups. Display as joined, but join via AJAX by default
        group_invites = self.user.groups_can_join()
        group_invites = list(set(group_invites))
        return self.render('user/user_welcome.html', # extends dashboard.html
            user = self.user, 
            nav_title = True,
            nav_select = 'dashboard',
            groups = None,
            group_invites = group_invites,
            recent_contacts = None, # not enough time for this script to execute
            today_reminders = None,
            later_reminders = None) # new users never have any reminders







