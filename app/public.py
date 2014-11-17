import app.basic, settings, ui_methods
import logging
import tornado.web
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from app.connectionsets import GroupConnectionSet, ProfileConnectionSet, BaseProfileConnection
from mongoengine.queryset import Q


########################
### Homepage
### /
########################
class Index(app.basic.BaseHandler):
  def get(self):
    return self.render('public/index.html')

########################
### Search
### /$
########################
class Search(app.basic.BaseHandler):
  @tornado.web.authenticated
  def get(self):
    name = self.get_argument('name', '')
    domain = self.get_argument('domain', '')

    if name or domain:
        # Global profile results
        profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

        # Connections
        current_user = User.objects.get(email=self.current_user)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by('-latest_email_out_date')

        # BaseProfileConnections for All tab 
        ps = []
        for p in profiles:
            bp = BaseProfileConnection(p)
            cs = Connection.objects(profile=p, user__in=group_users).order_by('-latest_email_out_date')
            if len(cs) > 0:
                bp.connections = cs
                bp.latest_email_out_date = cs[0]
            ps.append(bp)


        # De-dupe profiles that user is connected to
        # This is djanky because can't do joins :(
        '''
        ps = []
        for p in profiles:
            p_flag = True
            for c in connections:
                if p.id == c.profile.id:
                    p_flag = False
            if p_flag:
                ps.append(p)
        profiles = ps
        '''

        # Organize connections into dictionaries to handle multiple people being
        # connected to the same email
        profile_connection_set = ProfileConnectionSet.package_connections(connections)
        group_connection_set = GroupConnectionSet.package_connections(connections)

        return self.render('public/search.html', 
            profiles=ps,
            profile_connection_set=profile_connection_set,
            group_connection_set=group_connection_set,
            get_domain=ui_methods.get_domain,
            truncate=ui_methods.truncate)
    else:
        return self.redirect('/')


########################
### About 
### /about
########################
class About(app.basic.BaseHandler):
  def get(self):
    return self.render('public/about.html')

