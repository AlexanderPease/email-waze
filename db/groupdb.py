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

    # Ex: only @usv.com users can join
    domain_restriction = StringField()



    def __str__(self):
        if self.name:
            return self.name
        else:
            return "Group w/out name"


    def add_user(self, user):
        """
        Adds a User to the Group (w/out duplication)
        """
        if user not in self.users and self.check_domain_restriction(user):
            return self.users.append(user)


    def remove_user(self, user):
        """
        Removes a User in the Group
        """
        if user in self.users:
            return self.users.remove(user)


    def set_domain_restriction(self, domain):
        """
        Sets a domain restriction for the group.
        Ex: only @usv.com users can join.

        Returns:
            Group or None if failed
        """
        # Ensure that existing users belong in the group
        for u in self.users:
            if u.get_domain() not in domain:
                return None

        self.domain_restriction = domain
        return self

    def check_domain_restriction(self, user):
        """
        Checks if user is allowed to be added to the group based on self.settings

        Returns: True or None
        """
        if self.domain_restriction:
            if user.get_domain() in self.domain_restriction:
                return True

        return False





