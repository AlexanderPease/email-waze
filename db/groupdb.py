import settings, logging
from mongoengine import *
from userdb import User
from app.methods import send_email_template

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
                    self.invited_emails.remove(user.email)
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

    def num_users_string(self, plus_one=False):
        '''
        Returns string for how many Users this Group has
        Ex: "1 member" or "343 members"
        Does not include period at end of string.

        Args
            plus_one adds 1 to the number of users.
        '''
        num_users = len(self.users)
        if plus_one:
            num_users += 1
        if num_users == 1:
            return '1 member'
        else:
            return '%s members' % num_users

    def users_string(self, include_emails=True):
        '''
        Returns comma-delimited string of all Users
        Ex: "Alexander Pease (alex@foo.com), Nora Ali (nora@gmail.com)"
        '''
        group_members = ""
        first = True
        for group_member in self.users:
            if not first:
                group_members = group_members + ", "
            group_members = group_members + group_member.name
            if include_emails:
                group_members = group_members + " (" + group_member.email + ")"
            first = False
        return group_members

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

    def send_new_user_alert_emails(self, new_user):
        '''
        Sends an alert email to all existing Users of this Group that 
        User new_user has joined. 

        Call this method before the new_user has actually been added to self.users
        '''
        for group_user in self.users:
            subject = "%s joined your NTWRK!" % new_user.name
            merge_vars = [
               { 
                    'name': 'subject',
                    'content': subject,
                }, {
                    'name': 'new_user_name',
                    'content': new_user.name
                }, {
                    'name': 'new_user_email',
                    'content': new_user.email
                }, {
                    'name': 'group_name',
                    'content': self.name
                }, {
                    'name': 'group_href',
                    'content': '%s/user/settings' % settings.get('base_url')
                }, {
                    'name': 'num_members_string',
                    'content': self.num_users_string(plus_one=True)
                }, {
                    'name': 'member_list',
                    'content': self.users_string()
                }, {
                    'name': 'unsub',
                    'content': settings.get('base_url')
                }, {
                    'name': 'update_profile',
                    'content': settings.get('base_url')
                }
            ]
            send_email_template(
                template_name = 'new-user-alert',
                merge_vars = merge_vars,
                from_name = 'NTWRK',
                to_email = group_user.email,
                subject = subject)

    def send_just_accepted_invite_email(self, new_user):
        '''
        Email sent to the new_user (new or preexisting NTWRK User) 
        that just joined a Group
        '''
        subject = "You've joined %s!" % self.name
        merge_vars = [
           { 
                'name': 'subject',
                'content': subject,
            }, {
                'name': 'group_name',
                'content': self.name
            }, {
                'name': 'group_href',
                'content': '%s/user/settings' % settings.get('base_url')
            }, {
                'name': 'num_members_string',
                'content': self.num_users_string()
            }, {
                'name': 'member_list',
                'content': self.users_string()
            }, {
                'name': 'unsub',
                'content': settings.get('base_url')
            }, {
                'name': 'update_profile',
                'content': settings.get('base_url')
            }
        ]
        send_email_template(
            template_name = 'just-accepted-invite',
            merge_vars = merge_vars,
            from_name = 'NTWRK',
            to_email = new_user.email,
            subject = subject)



