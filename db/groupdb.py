import settings
from mongoengine import *
from userdb import User
import logging

mongo_database = settings.get('mongo_database')
connect('group', host=mongo_database['host'])


class Group(Document):
    # List of Users in the group. The User object also saves it's Groups. 
    users = ListField(ReferenceField(User))
    name = StringField()



    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Group w/out name"

    def add_user(user):
        """
        Adds a user to the Group
        """
        if user not in self.users:
            self.users

