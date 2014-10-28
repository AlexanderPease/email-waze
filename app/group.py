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
        domain_restriction = self.get_argument('domain_restriction', '')

        g = Group(name=name, 
                users=[current_user],
                admin=current_user, 
                domain_restriction=domain_restriction)

        # Add email invites
        if invited_emails:
            invited_emails = invited_emails.split(", ")
            g.invited_emails = invited_emails

        g.save()

        return self.redirect('/group/%s/edit' % g.id)

########################
### Edit a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/edit
########################
class EditGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group):
        try:
            g = Group.objects.get(id=group)
        except:
            pass #error

        # Only allow Group admin to make changes to Group
        u = User.objects.get(email=self.current_user)
        if g.admin not u:
            return self.render('/')

        return self.render('group/group_edit.html', g=g, 
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)

    @tornado.web.authenticated
    def post(self, group):
        name = self.get_argument('name', '')
        invited_emails = self.get_argument('invited_emails', '')
        domain_restriction = self.get_argument('domain_restriction', '')

        g = Group.objects.get(id=group)
        g.name = name
        g.domain_restriction = domain_restriction
        if not g.admin:
            g.admin = current_user

        # Add email invites
        if invited_emails:
            invited_emails = invited_emails.split(", ")
            g.invited_emails = invited_emails

        logging.info(g.invited_emails)

        g.save()

        return self.render('group/group_edit.html', g=g,
            list_to_comma_delimited_string=ui_methods.list_to_comma_delimited_string)

