import settings
from mongoengine import *
from userdb import User
from profiledb import Profile
from connectiondb import Connection
from companydb import Company
import logging, datetime
from math import fabs #absolute value

class ProfileReminder(Document):
    user = ReferenceField(User, required=True)
    profile = ReferenceField(Profile, required=True, unique_with='user')

    # Set automatically
    company = ReferenceField(Company) 
    connection = ReferenceField(Connection)

    # Number of days until reminder is due, or number of days for recurring time period
    days = IntField(required=True)

    # Recurring reminder or not
    recurring = BooleanField(required=True, default=False)

    # Date reminder was set
    date_set = DateTimeField(required=True, default=datetime.datetime.now())

    def save(self , *args, **kwargs):
        '''
        Automatically sets self.company and self.connection
        '''
        if not self.company:
            try:
                self.company = Company.objects.get(domain=self.profile.domain)
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

    def display_last_emailed(self):
        if not self.connection:
            return 'N/A (Reminder set %s)' % self.date_set.strftime('%Y/%m/%d')
        else:
            days_since = self.connection.days_since_emailed_out()
            if days_since < 30:
                return '%s days ago' % days_since
            else:
                return self.connection.latest_email_out_date_string()

    def display_due_date(self):
        """
        Calculates due date for display_due
        Ex: "Wednesday", "Next Thursday"
        """
        if self.connection:
            if self.connection.latest_email_out_date:
                latest_date = self.connection.latest_email_out_date
            else:
                latest_date = self.date_set
        else:
            latest_date = self.date_set
        days_left = (datetime.datetime.today() - latest_date) - datetime.timedelta(days=self.days)
        days_left = int(days_left.days)
        if days_left < -1:
            return 'Past (%s days ago)' % int(fabs(days_left))
        elif days_left == -1:
            return 'Past (Yesterday)'
        elif days_left == 0:
            return 'Today'
        elif days_left == 1:
            return 'Tomorrow'
        else:
            return 'In %s days' % days_left

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
            if latest_date + datetime.timedelta(days=pr.days) <= datetime.datetime.today():
                today_reminders.append(pr)
            else:
                later_reminders.append(pr)
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