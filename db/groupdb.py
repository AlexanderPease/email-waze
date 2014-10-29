import settings, logging
from mongoengine import *
from userdb import User

mongo_database = settings.get('mongo_database')
connect('group', host=mongo_database['host'])

class Group(Document):
    # List of Users in the group 
    users = ListField(ReferenceField(User), required=True)
    name = StringField()
    admin = ReferenceField(User)

    # List of emails that have been invited but haven't joined yet
    # Delete from this list as a User with this email join the Group
    invited_emails = ListField(EmailField())

    # Ex: All @usv.com users can find and join
    domain_setting = StringField()



    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Group w/out name"


    def add_user(self, user):
        """
        Adds a User to the Group (w/out duplication)
        """
        if user not in self.users or user.domain() in self.domain_setting:
            return self.users.append(user)


    def remove_user(self, user):
        """
        Removes a User in the Group
        """
        if user in self.users:
            return self.users.remove(user)





