import app.basic, settings, ui_methods
import logging
import tornado.web
import datetime
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
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
            nav_title=True,
            nav_select='dashboard',
            groups=gs,
            today_reminders=today_reminders,
            later_reminders=later_reminders)
    # Not logged in
    else:
        return self.render('public/index.html')

########################
### Search
### /$
########################
class Search(app.basic.BaseHandler):
  @tornado.web.authenticated
  def get(self):
    # Groups for advanced search
    gs = User.objects.get(email=self.current_user).get_groups()
    return self.render('public/search.html', 
        groups=gs, 
        nav_select='search',
        nav_title=True)

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
        nav_title="Reminders",
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


