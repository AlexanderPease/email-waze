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

        Returns Group if successfully added, None if rejected
        """
        if user not in self.users:
            if user.email in self.invited_emails or user.get_domain() in self.domain_setting:
                # Satisfied conditions to be added
                self.users.append(user)
                # Remove from invited_emails if applicable
                if user.email in self.invited_emails:
                    self.invited_emails.remove(u.email)
                return self


    def remove_user(self, user):
        """
        Removes a User in the Group

        Returns the group if successful, None if not
        """
        if user in self.users:
            if len(self.users) == 1:
                self.delete()
            elif self.admin.same_user(user):
                self.users.remove(user)
                self.admin = self.users[0]
            else:
                self.users.remove(user)
                return self

    def user_can_join(self, user):
        """
        Returns True if User is allowed to join. User CANNOT already be in Group. 
        Either invited or domain_setting is set. 
        """
        if user in self.users:
            return False
        if user.email in self.invited_emails or user.get_domain() in self.domain_setting:
            return True
        else:
            return False

    # TODO: fix users and admin, they are currently worthless entries
    # Just using name and id in user_welcome currently
    def to_json(self):
        """
        Converts instance into JSON dict
        """
        json = {'id': str(self.id),
            'users': [],
            'name': self.name,
            'admin': self.admin.to_json(),
            'invited_emails': self.invited_emails,
            'domain_setting': self.domain_setting
            }
        for u in self.users:
            json['users'].append(u.to_json())
        return json





