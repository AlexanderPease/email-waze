import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
from connectiondb import Connection
from companydb import Company
import logging, datetime
from math import fabs #absolute value
from app.methods import send_email_template

class ProfileReminder(Document):
    user = ReferenceField(User, required=True)
    profile = ReferenceField(Profile, required=True, unique_with='user')

    # Set automatically
    company = ReferenceField(Company) 
    connection = ReferenceField(Connection)

    # Date reminder was set
    date_set = DateTimeField(required=True, default=datetime.datetime.now())

    # Number of days from date_set until reminder is due, 
    #or number of days for recurring time period
    days = IntField(required=True)

    # Recurring reminder or not
    recurring = BooleanField(required=True, default=False)

    # Tracks number of times reminder email was sent
    emailed_reminder_due = IntField(required=True, default=0)

    def save(self , *args, **kwargs):
        '''
        Automatically sets self.company and self.connection
        '''
        if not self.company:
            try:
                company = Company.objects.get(domain=self.profile.domain)
                if company.name:
                    self.company = company
            except:
                pass
        if not self.connection:
            try:
                self.connection = Connection.objects.get(user=self.user, profile=self.profile)
            except:
                pass
        return super(ProfileReminder, self).save(*args, **kwargs)

    def __str__(self):
        return 'ProfileReminder: %s <-> %s' % (self.user, self.profile)

    def days_since_emailed(self):
        """
        Returns number of days since self.profile was last emailed. 
        If never emailed, returns arbitrarily high number of days. 
        """
        if not self.connection:
            return None
        else:
            return self.connection.days_since_emailed_out()

    def days_until_due(self):
        """
        Returns number of days until reminder is due. 
        Negative numbers if past due. 0 if due today
        """
        if self.connection:
            days_since = self.connection.days_since_emailed_out()
            if not days_since:
                days_since = (datetime.datetime.today() - self.date_set).days
        else:
            days_since = (datetime.datetime.today() - self.date_set).days
        return self.days - days_since
        #days_left = (latest_date.date() - datetime.datetime.today().date()) + datetime.timedelta(days=self.days)


###########################
### Methods for displaying
###########################
    def display_due_date(self):
        """
        Displays due date for to display
        Ex: "Wednesday", "Next Thursday"
        """
        days_left = self.days_until_due()
        if days_left < -1:
            return '%s days ago' % int(fabs(days_left))
        elif days_left == -1:
            return 'Yesterday'
        elif days_left == 0:
            return 'Today'
        elif days_left == 1:
            return 'Tomorrow'
        else:
            return 'In %s days' % days_left

    def display_alert_type(self):
        if self.recurring == True:
            if self.days == 7:
                return 'Weekly'
            elif self.days == 30:
                return 'Monthly'
            elif self.days == 90:
                return 'Quarterly'
            else:
                return 'Every %s days' % self.days
        else:
            return 'One time'

    def display_last_emailed(self, verbose=False):
        '''
        Returns a string to display when User last emailed Profile
        Args:
            verbose ensures returned string can be part of a sentence.
            Ex: '2014/01/01' becomes 'on 2014/01/01
        '''
        if not self.connection:
            return 'N/A (Reminder set %s)' % self.date_set.strftime('%Y/%m/%d')
        else:
            days_since = self.connection.days_since_emailed_out()
            if days_since < 30:
                if days_since == 1:
                    return '1 day ago'
                else:
                    return '%s days ago' % days_since
            else:
                if verbose:
                    return 'on ' + self.connection.latest_email_out_date_string()
                else:
                    return self.connection.latest_email_out_date_string()

    def sort_days_since_emailed(self):
        '''
        For sorting datatables. Returns arbitrarily high number of days
        if User has never emailed Profile before
        '''
        days = self.days_since_emailed()
        if not days:
            return 99999
        else:
            return days




###########################
### Emails
###########################
    def send_reminder_due_email(self):
        '''
        Email sent when a ProfileReminder is due
        '''
        subject = "Reminder for %s!" % self.profile.name
        merge_vars = [
            { 
                'name': 'subject',
                'content': subject
            }, { 
                'name': 'reminder_profile_name',
                'content': self.profile.name
            }, { 
                'name': 'reminder_profile_email',
                'content': self.profile.email
            }, { 
                'name': 'last_emailed',
                'content': self.display_last_emailed(verbose=True)
            }, { 
                'name': 'alert_type',
                'content': self.display_alert_type()
            }, { 
                'name': 'all_reminders_href',
                'content': settings.get('base_url') + '/reminders'
            }, {
                'name': 'unsub',
                'content': settings.get('base_url')
            }, {
                'name': 'update_profile',
                'content': settings.get('base_url')
            }
        ]
        send_email_template(
            template_name = 'reminder-due',
            merge_vars = merge_vars,
            from_name = 'NTWRK',
            to_email = self.user.email,
            subject = subject)
        self.emailed_reminder_due += 1
        self.save()

    def to_json(self):
        return {
            'days': self.days,
            'recurring': self.recurring, 
            'date_set': self.date_set.strftime('%Y/%m/%d'),
            'alert_type': self.display_alert_type()
        }

###########################
### Class methods
###########################
    @classmethod
    def today_later_reminders(cls, user):
        """
        Group a users reminders by due date, either today or later_reminders

        Returns:
            today_reminders is a list of Reminders that are due today (or previously)
            later_reminders is a list of Reminders that are due in future
        """
        prs = ProfileReminder.objects(user=user)
        today_reminders = []
        later_reminders = []
        for pr in prs:
            # Use connection.latest_email_out_date, default to date reminder was set 
            if pr.connection:
                if pr.connection.latest_email_out_date:
                    latest_date = pr.connection.latest_email_out_date
                else: 
                    latest_date = pr.date_set
            else:
                latest_date = pr.date_set
            # Group into reminders due today or later
            if latest_date.date() + datetime.timedelta(days=pr.days) > datetime.datetime.today().date():
                later_reminders.append(pr)
            else:
                today_reminders.append(pr)
        return today_reminders, later_reminders



class CompanyReminder(Document):
    user = ReferenceField(User, required=True)
    company = ReferenceField(Company, required=True, unique_with='user')
    recurring = BooleanField(required=True, default=False)
    date_set = DateTimeField(required=True, default=datetime.datetime.now())
    days = IntField(required=True)

    def __str__(self):
        return 'CompanyReminder: %s <-> %s' % (self.user, self.company)


class Reminder:
    def __init__(self, reminder):
        self.reminder = reminder # Either ProfileReminder or Company