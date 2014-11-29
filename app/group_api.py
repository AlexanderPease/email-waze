import app.basic, settings, ui_methods, tornado.web
import logging
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
from db.groupdb import Group
from connectionsets import GroupConnectionSet, ProfileConnectionSet
import connectionsets

########################
### User accepts a group invitation
### /api/(?P<group>[A-z-+0-9]+)/acceptinvite
########################
class AcceptInvite(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')
        group_id = self.get_argument('group_id', '')
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
            return self.api_response()
        else:
            return self.api_error(401, 'User is not allowed to join that team')




