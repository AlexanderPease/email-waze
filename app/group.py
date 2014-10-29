import app.basic, settings, ui_methods
import logging
import tornado.web
from db.groupdb import Group
from db.userdb import User

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
            g.invited_emails = invited_emails

        g.save()

        return self.redirect('/user/settings?msg=Successfully updated group settings!')


########################
### Edit a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/edit
########################
class EditGroup(app.basic.BaseHandler):
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
        u = User.objects.get(email=self.current_user)
        if not u.same_user(g.admin):
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
            g.invited_emails = invited_emails

        g.save()

        return self.redirect('/user/settings?msg=Successfully updated group settings!')


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

