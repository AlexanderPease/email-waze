import app.basic, settings, ui_methods, tornado.web
import logging
from db.userdb import User
from db.groupdb import Group
from methods import send_email_template

########################
### Create a new group
### /api/group/create
########################
class CreateGroup(app.basic.BaseHandler):
    '''
    @tornado.web.authenticated
    def get(self):
        return self.render('group/group_edit.html', g=None)
    '''

    @tornado.web.authenticated
    def post(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        name = self.get_argument('name', '')
        invited_emails = self.get_argument('invited_emails', '')
        domain_setting = self.get_argument('domain_setting', '')

        g = Group(name=name, 
                users=[current_user],
                admin=current_user,
                domain_setting=domain_setting)
        g.save()

        # Add email invites
        if invited_emails:
            invited_emails = invited_emails.split(", ")
            # Send invites to only newly invited emails
            old_invited_emails = g.invited_emails
            for e in invited_emails:
                if e not in old_invited_emails:
                    try:
                        existing_user = User.objects.get(email=e)
                    except:
                        existing_user = None
                    if existing_user:
                        self.send_invite_email_existing_user(
                            group = g, 
                            to_email = e, 
                            current_user = current_user)
                    else:
                        self.send_invite_email_new_user(
                            to_email = e,
                            current_user = current_user)
            # Set new invited_emails
            g.invited_emails = invited_emails
        elif g.invited_emails and invited_emails == "":
            g.invited_emails = []

        try:
            g.save()
        except:
            logging.warning("Error saving invited_emails")
            g.delete()
            return self.api_error(400, "err-invited-emails")

        return self.api_response(data={})

    def send_invite_email_new_user(self, to_email, current_user):
        """
        Sends invite email to a new user
        """
        merge_vars = [
           { 
                'name': 'subject',
                'content': 'Invitation from %s' % current_user.name
            }, { 
                'name': 'inviting_user_name',
                'content': current_user.name
            }, {
                'name': 'inviting_user_email',
                'content': current_user.email
            }, {
                'name': 'invite_href',
                'content': settings.get('base_url')
            }, {
                'name': 'unsub',
                'content': settings.get('base_url')
            }, {
                'name': 'unpdate_profile',
                'content': settings.get('base_url')
            }
        ]
        send_email_template(
            template_name = 'invite-new-user',
            merge_vars = merge_vars,
            from_name = '%s via NTWRK' % current_user.name,
            to_email = to_email,
            subject = 'Invitation from %s (%s)' % (current_user.name, current_user.email))

    def send_invite_email_existing_user(self, group, to_email, current_user):
        """
        Sends invite email to an existing user
        """
        # Print string of existing team members
        group_members = ""
        first = True
        for group_member in group.users:
            if not first:
                group_members = group_members + ", "
            group_members = group_members + group_member.name + " (" + group_member.email + ")"
            first = False
        if len(group.users) == 1:
            num_members_string = '1 member'
        else:
            num_members_string = '%s members' % len(group.users)
        merge_vars = [
           { 
                'name': 'subject',
                'content': 'Invitation from %s' % current_user.name
            }, { 
                'name': 'inviting_user_name',
                'content': current_user.name
            }, {
                'name': 'inviting_user_email',
                'content': current_user.email
            }, {
                'name': 'invite_href',
                'content': '%s/group/%s/acceptinvite' % (settings.get('base_url'), group.id)
            }, {
                'name': 'group_name',
                'content': group.name
            }, {
                'name': 'invite_href',
                'content': '%s/group/%s/acceptinvite' % (settings.get('base_url'), group.id)
            }, {
                'name': 'num_members_string',
                'content': num_members_string
            }, {
                'name': 'member_list',
                'content': group_members
            }, {
                'name': 'unsub',
                'content': settings.get('base_url')
            }, {
                'name': 'unpdate_profile',
                'content': settings.get('base_url')
            }
        ]
        send_email_template(
            template_name = 'invite-existing-user',
            merge_vars = merge_vars,
            from_name = '%s via NTWRK' % current_user.name,
            to_email = to_email,
            subject = 'Invitation from %s (%s)' % (current_user.name, current_user.email))
        """
        self.send_email(from_address='NTWRK <postmaster@ntwrk.me>',
            to_address=to_address,
            subject='Invitation from %s (%s)' % (current_user.name, current_user.email),
            html_text='''%s (%s) has invited you to join team
            "%s". A "NTWRK" allows a group of people to share contacts and connections
            with one another. 
            <a href="%s/group/%s/acceptinvite">Click here</a> 
            to join!</br></br>
            "%s" has %s members: %s.''' % (current_user.name, current_user.email, group.name, settings.get('base_url'), group.id, group.name, len(group.users), group_members)
            )
        """

########################
### Edit a group. Use group document id string as identifier. 
### /api/group/(?P<group>[A-z-+0-9]+)/edit
########################
class EditGroup(CreateGroup):
    @tornado.web.authenticated
    def post(self, group_id):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        name = self.get_argument('name', '')
        invited_emails = self.get_argument('invited_emails', '')
        domain_setting = self.get_argument('domain_setting', '')

        # Only allow Group admin to make changes to Group
        try:
            g = Group.objects.get(id=group_id)
        except:
            return self.api_error(500, 'Could not find group of id %s' % group_id)
        if not current_user.same_user(g.admin):
            return self.api_error(400, 'User is not a group admin')

        if name:
            g.name = name
        g.domain_setting = domain_setting 
        if not g.admin:
            g.admin = current_user
        g.save()

        # Add email invites
        if invited_emails:
            invited_emails = invited_emails.split(", ")
            # Send invites to only newly invited emails
            old_invited_emails = g.invited_emails
            for e in invited_emails:
                if e not in old_invited_emails:
                    try:
                        existing_user = User.objects.get(email=e)
                    except:
                        existing_user = None
                    if existing_user:
                        self.send_invite_email_existing_user(
                            group = g, 
                            to_email = e, 
                            current_user = current_user)
                    else:
                        self.send_invite_email_new_user(
                            to_email = e,
                            current_user = current_user)
            # Set new invited_emails
            g.invited_emails = invited_emails
        elif g.invited_emails and invited_emails == "":
            g.invited_emails = []

        try:
            g.save()
        except:
            logging.warning("Error saving invited_emails")
            return self.api_error(400, "Invited emails error")

        return self.api_response(data={})



########################
### User accepts a group invitation
### /api/group/(?P<group>[A-z-+0-9]+)/acceptinvite
########################
class AcceptInvite(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self, group_id):
        """
        User accepts a Group invite request. Adds User to the group, and sends
        emails both to the User as well as existing Group members
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            g = Group.objects.get(id=group_id)
        except:
            return self.api_error(500, 'Could not find group in database')

        if g.user_can_join(self.user):
            # Send emails to new member and existing members
            self.send_email(from_address='NTWRK <postmaster@ntwrk.me>',
                        to_address=self.user.email,
                        subject="You've joined %s!" % g.name,
                        html_text='''Congrats! You're now the newest member of
                        team "%s", along with %s other members. 
                        Click 
                        <a href="%s/group/%s/view">here</a> to see more info about the 
                        group.''' % (g.name, len(g.users), settings.get('base_url'), g.id)
                        )
            for group_user in g.users:
                self.send_email(from_address='NTWRK <postmaster@ntwrk.me>',
                        to_address=group_user.email,
                        subject="%s joined %s!" % (self.user.name, g.name),
                        html_text='''%s (%s) has joined you as a member of team "%s".
                        This means that you are now sharing contacts and email metadata
                        with %s. Click 
                        <a href="%s/group/%s/view">here</a> to view the 
                        your settings. </br>
                        "%s" now has %s members and is administered by %s 
                        (%s)''' % (self.user.name, self.user.email, g.name, self.user.name, settings.get('base_url'), g.id, g.name, len(g.users) + 1, g.admin.name, g.admin.email)
                        )
                # Number of members is len(g.users) + 1 b/c I add_user below. 
                # This makes it easy to email the right notifications

            g.add_user(self.user)
            g.save()
            return self.api_response(data={})
        else:
            return self.api_error(401, 'User is not allowed to join that team')

########################
### User leaves
### /api/group/(?P<group>[A-z-+0-9]+)/leave
########################
class Leave(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self, group_id):
        """
        User removes him/herself from the group
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            group = Group.objects.get(id=group_id)
        except:
            return self.api_error(500, 'Could not find group in database')
        group = group.remove_user(self.user)
        if group:
            group.save()
            return self.api_response(data={})
        else:
            return self.api_error(500, "Error leaving group. Possibly wasn't in Group!")

########################
### Group admin deletes the entire group
### /api/group/(?P<group>[A-z-+0-9]+)/delete
########################
class Delete(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self, group_id):
        """
        Group admin deletes the group
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')
        try:
            g = Group.objects.get(id=group_id)
        except:
            return self.api_error(500, 'Could not find group in database')
        if not g.admin == u:
            return self.api_error(400, 'User is not admin')
        g.delete()
        return self.api_response(data={})

