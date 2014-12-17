import app.basic, settings, ui_methods, tornado.web
import logging
from db.userdb import User
from db.groupdb import Group

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
                        self.send_invite_email_existing_user(group=g, 
                            to_address=e, 
                            current_user=current_user)
                    else:
                        self.send_invite_email_new_user(to_address=e,
                            current_user=current_user)
            # Set new invited_emails
            g.invited_emails = invited_emails
        elif g.invited_emails and invited_emails == "":
            g.invited_emails = []

        g.save()
        return self.api_response(data={})

    def send_invite_email_new_user(self, to_address, current_user):
        """
        Sends invite email to a new Ansatz user
        """
        self.send_email(from_address='Ansatz.me <postmaster@ansatz.me>',
            to_address=to_address,
            subject='Invitation from %s (%s)' % (current_user.name, current_user.email),
            html_text='''%s (%s) has invited you to join 
            <a href="%s">Ansatz.me</a>! 
            Ansatz is the anti-CRM: leverage your team's network
            and communication without any tedious data entry or 
            tracking. Visit 
            <a href="https://ansatz.me">https://ansatz.me</a> 
            to learn more!''' % (current_user.name, current_user.email, settings.get('base_url'))
            )

    def send_invite_email_existing_user(self, group, to_address, current_user):
        """
        Sends invite email to an existing Ansatz user
        """
        # Print string of existing team members
        group_members = ""
        first = True
        for group_member in group.users:
            if not first:
                group_members = group_members + ", "
            group_members = group_members + group_member.name + " (" + group_member.email + ")"
            first = False
        # Send email
        self.send_email(from_address='Ansatz.me <postmaster@ansatz.me>',
            to_address=to_address,
            subject='Invitation from %s (%s)' % (current_user.name, current_user.email),
            html_text='''%s (%s) has invited you to join team
            "%s". 
            <a href="%s/group/%s/acceptinvite">Click here</a> 
            to join!</br></br>
            Team "%s" has %s members: %s.''' % (current_user.name, current_user.email, group.name, settings.get('base_url'), group.id, group.name, len(group.users), group_members)
            )


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
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')
        try:
            g = Group.objects.get(id=group_id)
        except:
            return self.api_error(500, 'Could not find group in database')

        if u.email in g.invited_emails or u.get_domain() in g.domain_setting:
            # Send emails to new member and existing members
            self.send_email(from_address='Ansatz.me <postmaster@ansatz.me>',
                        to_address=u.email,
                        subject="You've joined %s!" % g.name,
                        html_text='''Congrats! You're now the newest member of
                        team "%s", along with %s other members. 
                        Click 
                        <a href="%s/group/%s/view">here</a> to see more info about the 
                        group.''' % (g.name, len(g.users), settings.get('base_url'), g.id)
                        )
            for group_user in g.users:
                self.send_email(from_address='Ansatz.me <postmaster@ansatz.me>',
                        to_address=group_user.email,
                        subject="%s joined %s!" % (u.name, g.name),
                        html_text='''%s (%s) has joined you as a member of team "%s".
                        This means that you are now sharing contacts and email metadata
                        with %s. If you want to remove yourself from the team, 
                        <a href="%s/group/%s/view">click here</a>. </br>
                        Team "%s" now has %s members and is administered by %s 
                        (%s)''' % (u.name, u.email, g.name, u.name, settings.get('base_url'), g.id, g.name, len(g.users) + 1, g.admin.name, g.admin.email)
                        )
                # Number of members is len(g.users) + 1 b/c I add_user below. 
                # This makes it easy to email the right notifications

            # Add user and remove from invited email list
            g.add_user(u)
            if u.email in g.invited_emails:
                g.invited_emails.remove(u.email)
            g.save()
            return self.api_response(data={})
        else:
            return self.api_error(401, 'User is not allowed to join that team')



