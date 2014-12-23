import app.basic, settings, ui_methods
import logging
import tornado.web
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from app.connectionsets import GroupConnectionSet, ProfileConnectionSet, BaseProfileConnection
from mongoengine.queryset import Q
import math

RESULTS_PER_PAGE = 20

########################
### tets
### /
########################
class Test(app.basic.BaseHandler):
  def get(self):
    return self.render('test.html')

########################
### Homepage
### /
########################
class Index(app.basic.BaseHandler):
  def get(self):
    err = self.get_argument('err', '')
    if err == 'no_results':
        err = 'No results found! Try another search'
    return self.render('public/index.html', err=err)

########################
### Search
### /$
########################
class Search(app.basic.BaseHandler):
  @tornado.web.authenticated
  def get(self):
    #return self.render('public/search_empty.html')
    name = self.get_argument('name', '')
    domain = self.get_argument('domain', '')
    #page = self.get_argument('page', '')

    if name or domain:
        # Global profile results
        profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

        # Pagination and no results
        if len(profiles) == 0:
            return self.redirect('/?err=no_results')
        '''
        elif len(profiles) > RESULTS_PER_PAGE:
            # Get page number
            num_pages = int(math.ceil(float(len(profiles)) / RESULTS_PER_PAGE))
            if page:
                page = int(page)
                start = (page - 1) * RESULTS_PER_PAGE
            else:
                page = 1
                start = 0
            end = start + RESULTS_PER_PAGE
            profiles = profiles[start:end]
        else:
            page = None
            num_pages = None
        '''

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
            #page=page,
            #num_pages=num_pages,
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

