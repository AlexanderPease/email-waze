import app.basic, settings, ui_methods, tornado.web
import logging
from db.reminderdb import ProfileReminder
from db.reminderdb import CompanyReminder
from db.userdb import User
from db.profiledb import Profile
from db.companydb import Company

########################
### User deletes his/her account
### /api/reminder/create
########################
class CreateReminder(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
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
        if recurring and recurring != "":
            recurring = True

        # Require necessary fields
        if profile_id and company_id:
            return self.api_error(400, 'Cannot set both company and profile')
        elif not profile_id and not company_id: 
            return self.api_error(400, 'Must have either company or profile')
        if not days:
            return self.api_error(400, 'Must set a reminder time period')

        # Save reminder
        if profile_id:
            try:
                p = Profile.objects.get(id=profile_id)
                logging.info(p)
            except:
                return self.api_error(501, 'Profile_ID is invalid')
            if p.email == u.email:
                return self.api_error(501, 'User cannot set reminder about him/herself')
            try:
                r = ProfileReminder(profile=p, user=u, days=days, recurring=recurring)
                r.save()
            except: 
                return self.api_error(501, 'Error saving profile reminder')
        elif company_id:
            try:
                c = Company.objects.get(id=company_id)
            except:
                return self.api_error(501, 'Company_ID is invalid')
            try:
                r = CompanyReminder(company=c, user=u, days=days, recurring=recurring)
                r.save()
            except: 
                return self.api_error(501, 'Error saving profile reminder')
        return self.api_response(data={})




