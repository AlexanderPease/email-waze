import app.basic, settings, ui_methods, tornado.web
import logging
from db.reminderdb import Reminder
from db.userdb import User

########################
### User deletes his/her account
### /api/reminder/create
########################
class CreateReminder(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, user_id):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Get args
        profile_id = self.get_argument('profile_id', '')
        company_id = self.get_argument('company_id', '')
        days = self.get_argument('days', '')
        recurring = self.get_argument('recurring', '')

        # Require necessary fields
        if profile_id and company_id:
            return self.api_error(400, 'Cannot set both company and profile')
        elif not profile_ud and not company_id: 
            return self.api_error(400, 'Must have either company or profile')
        if not days:
            return self.api_error(400, 'Must set a reminder time period')

        # Save reminder
        if profile_id:
            try:
                r = Reminder(profile=p, user=u, days=days, recurring=recurring)
            except: 
                return self.api_error(501, 'Error saving profile reminder')
        elif company_id:
            try:
                r = Reminder(company=c, user=u, days=days, recurring=recurring)
            except: 
                return self.api_error(501, 'Error saving profile reminder')
        return self.api_response(data={})




