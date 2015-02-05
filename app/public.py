import app.basic, settings, ui_methods
import logging
import tornado.web
import datetime
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from app.connectionsets import GroupConnectionSet, ProfileConnectionSet, BaseProfileConnection
from db.companydb import Company
from db.reminderdb import ProfileReminder, CompanyReminder
from mongoengine.queryset import Q
import math

RESULTS_PER_PAGE = 20

########################
### Homepage
### /
########################
class Index(app.basic.BaseHandler):
  def get(self):
    msg = self.get_argument('msg', '')
    if msg == 'welcome_back':
        msg = "Welcome back! It will take another few minutes to reextract your email metadata from Gmail"
    err = self.get_argument('err', '')
    if err == 'no_results':
        err = 'No results found! Try another search'

    # Logged in
    if self.user:
        gs = self.user.get_groups()
        today_reminders, later_reminders = ProfileReminder.today_later_reminders(user=self.user)
        return self.render('public/dashboard.html', 
            msg=msg, 
            err=err,
            groups=gs,
            today_reminders=today_reminders,
            later_reminders=later_reminders)
    # Not logged in
    else:
        return self.render('public/index.html', 
            msg=msg, 
            err=err,
            groups=None,
            today_reminders=None,
            later_reminders=None)

########################
### Search
### /$
########################
class Search(app.basic.BaseHandler):
  @tornado.web.authenticated
  def get(self):
    # Groups for advanced search
    gs = User.objects.get(email=self.current_user).get_groups()
    return self.render('public/search.html', groups=gs, nav_select="search")

"""
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

        # Company info
        if domain:
            companies = Company.objects(domain__icontains=domain)
        else:
            companies = None

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
"""

########################
### Reminders
### /about
########################
class Reminders(app.basic.BaseHandler):
  @tornado.web.authenticated
  def get(self):
    u = User.objects.get(email=self.current_user)
    today_reminders, later_reminders = ProfileReminder.today_later_reminders(user=u)
    return self.render('public/reminders.html',
        nav_select="reminders",
        today_reminders=today_reminders, 
        later_reminders=later_reminders)

########################
### About 
### /about
########################
class About(app.basic.BaseHandler):
  def get(self):
    return self.render('public/about.html')


########################
### Pricing
### /pricing
########################
class Pricing(app.basic.BaseHandler):
  def get(self):
    return self.render('public/pricing.html')


