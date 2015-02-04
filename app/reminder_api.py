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
        reminder_type = self.get_argument('reminder_type', '')
        doc_id = self.get_argument('doc_id', '')
        days = self.get_argument('days', '')
        recurring = self.get_argument('recurring', '')
        if recurring and recurring != "":
            recurring = True

        # Require necessary fields
        if not reminder_type or not doc_id or not days:
            return self.api_error(400, 'Invalid arg parameters')

        # Save reminder
        if reminder_type == 'profile':
            try:
                p = Profile.objects.get(id=doc_id)
            except:
                return self.api_error(400, 'Profile ID is invalid')
            if p.email == u.email:
                return self.api_error(400, 'User cannot set reminder about him/herself')
            try:
                r = ProfileReminder(profile=p, user=u, days=days, recurring=recurring)
                r.save()
            except: 
                return self.api_error(500, 'Error saving ProfileReminder')
        elif reminder_type == 'company':
            try:
                c = Company.objects.get(id=doc_id)
            except:
                return self.api_error(400, 'Company ID is invalid')
            #try:
            logging.info(c)
            logging.info(u)
            r = CompanyReminder(company=c, user=u, days=days, recurring=recurring)
            logging.info(r)
            r.save()
            #except: 
            #    return self.api_error(500, 'Error saving CompanyReminder')
        else:
            return self.api_error(400, 'Invalid reminder_type parameter')
        return self.api_response(data={})


########################
### Edit reminder
### /api/reminder/<reminder_id>/edit
########################
class EditReminder(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, reminder_id):
        """
        Required Args:
            reminder_type is either 'profile' or 'company'
        Args:
            days
            recurring should be set to 'true' or 'false'
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Get args
        reminder_type = self.get_argument('reminder_type', '')
        days = self.get_argument('days', '')
        recurring = self.get_argument('recurring', '')

        # Get reminder
        if reminder_type == 'profile':
            try:
                r = ProfileReminder.objects.get(id=reminder_id, user=u)
            except:
                return self.api_error(400, 'Invalid reminder_id parameter for ProfileReminder')
        elif reminder_type == 'company':
            try:
                r = CompanyReminder.objects.get(id=reminder_id, user=u)
            except:
                return self.api_error(400, 'Invalid reminder_id parameter for CompanyReminder')

        # Update reminder
        if days:
            r.days = days
        if recurring == 'false' or recurring == 'False':
            r.recurring = False
        elif recurring and recurring != "":
            r.recurring = True
        try:
            r.save()
            logging.info(r)
        except:
            return self.api_error(500, 'Error editing Reminder of type %s and id %s' %(reminder_type, reminder_id))

        return self.api_response(data={})


########################
### Delete the reminder
### /api/reminder/<reminder_id>/delete
########################
class DeleteReminder(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, reminder_id):
        """
        Required Args:
            reminder_type is either 'profile' or 'company'
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            u = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # reminder_type
        reminder_type = self.get_argument('reminder_type', '')
        if reminder_type != 'profile' and reminder_type != 'company':
            return self.api_error(500, 'Invalid reminder_type parameter')

        # Get reminder
        if reminder_type == 'profile':
            try:
                r = ProfileReminder.objects.get(id=reminder_id, user=u)
            except:
                return self.api_error(400, 'Invalid reminder_id parameter for ProfileReminder')
        elif reminder_type == 'company':
            try:
                r = CompanyReminder.objects.get(id=reminder_id, user=u)
            except:
                return self.api_error(400, 'Invalid reminder_id parameter for CompanyReminder')
        r.delete()
        return self.api_response(data={})



