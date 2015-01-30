import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
from companydb import Company
import logging, datetime

mongo_database = settings.get('mongo_database')
connect('reminder', host=mongo_database['host'])

class Reminder(Document):
    # The User who set the reminder
    user = ReferenceField(User, required=True)

    # Reminder is either to contact a Profile or Company
    # One of these is required
    profile = ReferenceField(Profile)
    company = ReferenceField(Company)

    # Recurring reminder or not
    recurring = BooleanField(required=True, default=False)

    # Date reminder was set
    date_set = DateTimeField(required=True, default=datetime.datetime.now())

    # Number of days until reminder is due, or number of days for recurring time period
    days = IntField(required=True)

    def __str__(self):
        if self.profile:
            return 'Reminder: User %s <-> Profile %s' % (self.user, self.profile)
        elif self.company:
            return 'Reminder: User %s <-> Company %s' % (self.user, self.company)
        else:
            raise Exception

    def clean(self):
        """
        Called before executing validate() as part of save()
        """
        # Ensure either company or profile is set
        if not self.profile and not self.company:
            raise Exception
        elif self.profile and self.company:
            raise Exception
        # Ensure sparse uniqueness. Couldn't get index to work
        if self.profile:
            rs = Reminder.objects(user=self.user, profile=self.profile)
        else:
            rs = Reminder.objects(user=self.user, company=self.company)
        if rs:
            if len(rs) > 1:
                raise Exception
            r = rs[0]
            if r.id != self.id:
                raise Exception



    def to_json(self):
        json = {}
        for k,v in Reminder._fields.iteritems():
            logging.info(self.k)
            logging.info(self.v) # ??
        return json

