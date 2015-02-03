import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
from companydb import Company
import logging, datetime

class Reminder(Document):
    user = ReferenceField(User, required=True)

    # Recurring reminder or not
    recurring = BooleanField(required=True, default=False)

    # Date reminder was set
    date_set = DateTimeField(required=True, default=datetime.datetime.now())

    # Number of days until reminder is due, or number of days for recurring time period
    days = IntField(required=True)

    def to_json(self):
        json = {}
        for k,v in Reminder._fields.iteritems():
            logging.info(self.k)
            logging.info(self.v) # ??
        return json

class CompanyReminder(Reminder):
    company = ReferenceField(Company, required=True)
    meta = {
        'indexes': [
            {'fields': ['user', 'company'], 'unique': True},
        ]
    }

    def __str__(self):
        return 'Reminder: User %s <-> Company %s' % (self.user, self.company)

class ProfileReminder(Reminder):
    profile = ReferenceField(Profile, required=True)
    meta = {
        'indexes': [
            {'fields': ['user', 'profile'], 'unique': True},
        ]
    }

    def __str__(self):
        return 'Reminder: User %s <-> Profile %s' % (self.user, self.profile)


