import app.basic, settings, ui_methods
import logging
import tornado.web
from db.groupdb import Group
from db.userdb import User
from db.connectiondb import Connection

########################
### Create a new group
### /group/create
########################
class CreateGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render('group/group_edit.html', g=None)

    @tornado.web.authenticated
    def post(self):
        logging.info('Creating a new group')
        current_user = User.objects.get(email=self.current_user)

        name = self.get_argument('name', '')
        invited_emails = self.get_argument('invited_emails', '')
        domain_setting = self.get_argument('domain_setting', '')

        g = Group(name=name, 
                users=[current_user],
                admin=current_user,
                domain_setting=domain_setting)

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
        return self.redirect('/user/settings?msg=Successfully updated group settings!')

    def send_invite_email_new_user(self, to_address, current_user):
        """
        Sends invite email to a group to a new Ansatz user
        """
        self.send_email(from_address='Ansatz.me <postmaster@ansatz.me>',
            to_address=to_address,
            subject='Invitation from %s (%s)' % (current_user.name, current_user.email),
            html_text='''%s has invited you to join 
            <a href="%s">Ansatz.me</a>! 
            Ansatz is the anti-CRM: leverage your team's network
            and communication without any tedious data entry or 
            tracking. Visit 
            <a href="https://ansatz.me">https://ansatz.me</a> 
            to learn more!''' % (settings.get('base_url'), current_user.name)
            )

    def send_invite_email_existing_user(self, group, to_address, current_user):
        """
        Sends invite email to a group to an existing Ansatz user
        """
        # Print string of existing team members
        group_members = ""
        first = True
        for group_member in g.users:
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
            <a href="%s/group/%s/acceptinvite"Click here</a> 
            to join!</br>
            Team %s has %s members: %s.''' % (current_user.name, current_user.email, settings.get('base_url'), group.id, group.name, len(group.users), group_members)
            )

########################
### Edit a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/edit
########################
class EditGroup(CreateGroup):
    @tornado.web.authenticated
    def get(self, group):
        # Only allow Group admin to make changes to Group
        g = Group.objects.get(id=group)
        u = User.objects.get(email=self.current_user)
        if not u.same_user(g.admin):
            return self.redirect('/')

        return self.render('group/group_edit.html', g=g, 
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)

    @tornado.web.authenticated
    def post(self, group):
        # Only allow Group admin to make changes to Group
        g = Group.objects.get(id=group)
        current_user = User.objects.get(email=self.current_user)
        if not current_user.same_user(g.admin):
            return self.redirect('/')

        name = self.get_argument('name', '')
        invited_emails = self.get_argument('invited_emails', '')
        domain_setting = self.get_argument('domain_setting', '')

        g.name = name
        g.domain_setting =domain_setting 
        if not g.admin:
            g.admin = current_user

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
                        self.send_invite_email_new_user(to_address=to_address,
                            current_user=current_user)
            # Set new invited_emails
            g.invited_emails = invited_emails
        elif g.invited_emails and invited_emails == "":
            g.invited_emails = []

        g.save()
        return self.redirect('/user/settings?msg=Successfully updated group settings!')

########################
### View a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/view
########################
class ViewGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group):
        g = Group.objects.get(id=group)
        u = User.objects.get(email=self.current_user)
        if not u in g.users:
            return self.redirect('/')

        return self.render('group/group_view.html', g=g, 
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)


########################
### Accept a group invitation. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/acceptinvite
########################
class AcceptGroupInvite(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group):
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.render("/?err=You need to log in first!")

        try:
            g = Group.objects.get(id=group)
        except:
            return self.redirect("/user/settings?err=Could not find team!")

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
                        (%s)''' % (u.name, u.email, g.name, u.name, settings.get('base_url'), g.id, g.name, len(g.users), g.admin.name, g.admin.email)
                        )

            # Add user and remove from invited email list
            g.add_user(u)
            logging.info(g.users)
            if u.email in g.invited_emails:
                g.invited_emails.remove(u.email)
            g.save()
            return self.redirect("/user/settings?msg=You've been added to the team!")
        else:
            return self.redirect("/user/settings?err=Not allowed to join that team!")


########################
### Delete a group 
### /group/(?P<group>[A-z-+0-9]+)/delete
########################
class DeleteGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self, group):
        # Only allow Group admin to delete Group
        g = Group.objects.get(id=group)
        u = User.objects.get(email=self.current_user)
        if not u.same_user(g.admin):
            return self.redirect('/')

        g.delete()
        return self.redirect("/user/settings?msg=You deleted the team :(")

