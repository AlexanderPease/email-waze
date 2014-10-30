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
        # Global profile results
        profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

        # Connections
        current_user = User.objects.get(email=self.current_user)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by('-total_emails_out')

        # De-dupe profiles that user is connected to
        # This is djanky because can't to joins :(
        ps = []
        for p in profiles:
            p_flag = True
            for c in connections:
                if p.id == c.profile.id:
                    p_flag = False
            if p_flag:
                ps.append(p)
        profiles = ps

        return self.render('public/index.html', profiles=profiles, connections=connections, email_obscure=Profile.get_domain)
    else:
        return self.render('public/index.html', profiles=None, connections=None)


class About(app.basic.BaseHandler):
  def get(self):
    return self.render('public/about.html')

