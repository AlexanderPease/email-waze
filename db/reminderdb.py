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

    # Allow subclassing
    meta = {'allow_inheritance': True}

    # Unfinished
    def to_json(self):
        json = {}
        for k,v in Reminder._fields.iteritems():
            logging.info(self.k)
            logging.info(self.v) # ??
        return json

    @classmethod
    def get_by_id(cls, reminder_type, reminder_id):
        """
        Returns ProfileReminder or CompanyReminder, or None if DNE
        """
        r = None
        logging.info(reminder_type)
        logging.info(reminder_id)
        if reminder_type == 'profile':
            try:
                r = ProfileReminder.objects.get(id=reminder_id)
            except:
                pass
        elif reminder_type == 'company':
            try:
                r = CompanyReminder.objects.get(id=reminder_id)
            except:
                pass
        return r

class ProfileReminder(Reminder):
    profile = ReferenceField(Profile, required=True, unique_with='user')

    def __str__(self):
        return 'Reminder: %s <-> %s' % (self.user, self.profile)

class CompanyReminder(Reminder):
    company = ReferenceField(Company, required=True, unique_with='user')

    def __str__(self):
        return 'Reminder: %s <-> %s' % (self.user, self.company)


