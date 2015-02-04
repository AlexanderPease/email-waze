import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
from companydb import Company
import logging, datetime

class ProfileReminder(Document):
    user = ReferenceField(User, required=True)
    profile = ReferenceField(Profile, required=True, unique_with='user')
    company = ReferenceField(Company) # Set automatically

    # Recurring reminder or not
    recurring = BooleanField(required=True, default=False)

    # Date reminder was set
    date_set = DateTimeField(required=True, default=datetime.datetime.now())

    # Number of days until reminder is due, or number of days for recurring time period
    days = IntField(required=True)

    def save(self , *args, **kwargs):
        '''
        Automatically sets self.company
        '''
        if not self.company:
            try:
                self.company = Company.objects.get(domain=self.profile.domain)
            except:
                pass
        return super(ProfileReminder, self).save(*args, **kwargs)

    def __str__(self):
        return 'ProfileReminder: %s <-> %s' % (self.user, self.profile)

class CompanyReminder(Document):
    user = ReferenceField(User, required=True)
    company = ReferenceField(Company, required=True, unique_with='user')
    recurring = BooleanField(required=True, default=False)
    date_set = DateTimeField(required=True, default=datetime.datetime.now())
    days = IntField(required=True)

    def __str__(self):
        return 'CompanyReminder: %s <-> %s' % (self.user, self.company)


class Reminder:
    def __init__(self, reminder):
        self.reminder = reminder # Either ProfileReminder or Company