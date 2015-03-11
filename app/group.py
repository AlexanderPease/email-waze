import app.basic, settings, ui_methods
import logging
import tornado.web
from db.groupdb import Group
from db.userdb import User
from db.connectiondb import Connection

########################
### Accept a group invitation. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/acceptinvite
########################
class AcceptGroupInvite(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group_id):
        try:
            group = Group.objects.get(id=group_id)
        except:
            return self.redirect("/user/settings?err=Could not find NTWRK!")

        if group.user_can_join(self.user):
            # Send emails to new member and existing members
            group.send_just_accepted_invite_email(self.user)
            group.send_new_user_alert_emails(self.user)
            # Add accepting user to group
            group.add_user(self.user)
            group.save()
            return self.redirect("/user/settings?msg=You've been added to %s!" % group.name)
        else:
            return self.redirect("/user/settings?err=You're not allowed to join %s!" % group.name)

########################
### Create a new group
### /group/create
########################
'''
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
        return self.redirect('/user/settings?msg=Successfully updated group settings!')

'''

########################
### Edit a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/edit
########################
'''
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
        return self.redirect('/user/settings?msg=Successfully updated group settings!')
'''

########################
### View a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/view
########################
'''
class ViewGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group):
        g = Group.objects.get(id=group)
        u = User.objects.get(email=self.current_user)
        if not u in g.users:
            return self.redirect('/')

        return self.render('group/group_view.html', g=g, 
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)
'''

########################
### Delete a group 
### /group/(?P<group>[A-z-+0-9]+)/delete
########################
'''
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
'''

