import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from mongoengine.queryset import Q


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    name = self.get_argument('name', '')
    domain = self.get_argument('domain', '')

    
    if name or domain:
        # Global results
        profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

        # Group users
        current_user = User.objects.get(email=self.current_user)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users)
        return self.render('public/index.html', results=profiles, connections=connections, email_obscure=Profile.get_domain)
    else:
        return self.render('public/index.html', results=None, connections=None)

