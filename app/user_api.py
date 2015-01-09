import app.basic, settings, ui_methods, tornado.web
import logging
from db.userdb import User
from db.groupdb import Group

########################
### User deletes his/her account
### /api/user/(?P<user_id>[A-z-+0-9]+)/deleteaccount
########################
class DeleteAccount(app.basic.BaseHandler):
    @tornado.web.authenticated
    def post(self, user_id):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Leave all teams
        groups = u.get_groups()
        for g in groups:
            g.remove_user(u)
            g.save()

        # Mark account as deleted
        u.deleted = True
        u.save()
        logging.info(u.deleted)

        return self.api_response(data={})




