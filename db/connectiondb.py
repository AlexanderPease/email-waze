import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
import logging, datetime

mongo_database = settings.get('mongo_database')
connect('connection', host=mongo_database['host'])


class Connection(Document):
    # The User who has corresponded with... 
    user = ReferenceField(User, required=True)

    # ...the email address of this Profile
    profile = ReferenceField(Profile, required=True) 

    total_emails_in = IntField()
    total_emails_out = IntField()
    latest_email_in_date = DateTimeField()
    latest_email_out_date = DateTimeField()

    # Last time a job was run that updated this document
    # Jobs should be User-first
    last_updated = DateTimeField()

    # Compound index so that pair of self.user and self.profile must be unique
    meta = {
        'indexes': [
            {'fields': ['user', 'profile'], 'unique': True},
        ]
    }


    def __str__(self):
        return 'Connection: User %s <-> Profile %s' % (self.user, self.profile)
