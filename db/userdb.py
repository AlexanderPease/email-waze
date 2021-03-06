import settings
from mongoengine import *
import httplib2, logging
import datetime
import random
# Google API OAUTH2 dependencies
from oauth2client.client import OAuth2Credentials
from googleapiclient.discovery import build 
import gdata.gauth 
import gdata.contacts.client

mongo_database = settings.get('mongo_database')
connect('user', host=mongo_database['host'])

def generate_api_key():
    """
    Generates an api key not currently being used by any User object
    """
    while True:
        api_key = '%030x' % random.randrange(16**30)
        try:
            user = User.objects.get(api_key=api_key)
        except:
            return api_key

class User(Document):
    # Email is the unique key and the username
    email = EmailField(required=True, unique=True) 
    name = StringField(required=True)
    given_name = StringField()
    family_name = StringField()
    api_key = StringField(required=True, default=generate_api_key())

    # Everything comes from Google OAuth2
    # Saved by OAuth2Credentials.to_json()
    google_credentials = StringField(required=True)
    # Save OAUTH_SCOPE for each user, in case this evolves
    google_credentials_scope = StringField(required=True) 

    # Stripe customer ID number
    stripe_id = StringField()
    stripe_subscription_id = StringField()

    # Date user joined the app
    joined = DateTimeField()
    # Has user been through welcome onboarding process?
    welcomed = BooleanField()

    # True when tasks.onboard_user completes
    # That task also sets last_updated
    onboarded = BooleanField()

    # Date user last had update_user() task run OR if just onboarded
    # the date that onboard_user() finished
    last_updated = DateTimeField()

    # Date the user last took an action in the web app
    last_web_action = DateTimeField()

    # True if user has deleted account
    deleted = BooleanField()


    def __str__(self):
        return 'User: ' + self.name + ' <' + self.email + '>'

    def to_json(self):
        """
        JSON representation of instance
        """
        return {
            'email': self.email,
            'name': self.name
        }

    def casual_name(self):
        if self.given_name and self.given_name is not "":
            return self.given_name
        else:
            return self.name

    def get_groups(self):
        """
        Returns a list of Groups the User is in
        """
        from groupdb import Group # B/c of circular dependency
        return Group.objects(users=self).order_by('name')


    def all_group_users(self, include_self=True):
        """
        Returns a distinct list of Users in all of the groups 
        that the User is a part of. Includes self in that list unless 
        exclude_self = False.
        """
        groups = self.get_groups()
        if len(groups) == 0:
            # If user has no groups, include self as only user
            all_users = [self]
        else:
            all_users = set([u for g in groups for u in g.users])

        # Flag to exclude self from list of users
        if not include_self:
            try:
                all_users.remove(self)
            except KeyError:
                pass # self was not in the set

        return list(all_users)

    def get_domain(self):
        """
        Returns just the domain name of self.email
        Ex: usv.com from foo@usv.com
        """
        return self.email.split('@')[1]

    def recent_contacts(self, num_contacts=20):
        """
        Returns a list of most recently emailed out BaseProfileConnections

        Args:
            num_contacts is the number of BaseProfileConnections to return
        """
        from connectiondb import Connection
        from app.connectionsets import BaseProfileConnection #b/c circular dependency
        cs = Connection.objects(user=self).order_by('-latest_email_out_date')
        if cs:
            cs = cs[0:num_contacts]
            bp_array = []
            for c in cs:
                bp_cs = Connection.objects(profile=c.profile, user=c.user)
                bp = BaseProfileConnection(profile=c.profile, 
                    connections=bp_cs,
                    current_user=c.user)
                bp_array.append(bp)
            return bp_array

    def same_user(self, u):
        """ 
        Returns True if the two User objects are the same Document, or False if not.
        """
        return self.id == u.id

    def recent_gmail(self):
        '''
        Checks all recent emails from Gmail and creates GmailMessageJobs
        to be processed
        '''
        # B/c circular dependency
        import app.gmail as gmail 
        from gmailmessagejobdb import GmailMessageJob

        logging.info("Starting recent_gmail() for %s" % self)
        gmail_service = self.get_service(service_type='gmail')
        if not gmail_service:
            logging.info("Could not instantiate authenticated service for %s" % self)
            return
        now = datetime.datetime.now() # To not miss emails created during running of this job
        messages = gmail.ListMessagesMatchingQuery(
            service=gmail_service,
            user_id='me',
            query='after:%s' % self.last_updated.strftime('%Y/%m/%d'))
         # Track list of emails that have been updated by this function
        for msg in messages:
            # May have already checked this message, since can only query Gmail
            # by date, not exact datetime. 
            g, created_flag = GmailMessageJob.objects.get_or_create(
                user = self,
                message_id = msg['id'],
                thread_id = msg['threadId'])
        # Save completed job specs to user
        self.last_updated = now
        self.save()
        logging.info("Finished recent_gmail() for %s" % self)

    def groups_can_join(self):
        """
        Returns a list of Groups this User can join. 
        Does not include Groups the User is already in
        """
        from groupdb import Group
        groups_can_join = []
        groups_invited = Group.objects(invited_emails=self.email)
        groups_domain =  Group.objects(domain_setting__icontains=self.get_domain())
        for g in list(groups_invited) + list(groups_domain):
            if self not in g.users:
                groups_can_join.append(g)
        return groups_can_join

    def get_service(self, service_type='gmail', version='v1'):
        """
        Returns Google service object for calling APIs

        Args: 
            service_type: Default 'gmail', or use 'oauth2' or 'plus'.

        Returns:
            googleapiclient.discovery.Resource instance or None if failed. 
        """
        credentials = OAuth2Credentials.new_from_json(self.google_credentials)
        http = httplib2.Http()
        if credentials is None or credentials.invalid:
            logging.warning('Credentials DNE or invalid')
        elif credentials.access_token_expired:
            # Refresh and save new access token if necessary
            if not credentials.refresh_token:
                logging.warning('No refresh token for expired credentials of %s' % self)
                return
            logging.info('refresh token:')
            logging.info("Access token: %s" % credentials.access_token)
            logging.info("Refresh token: %s" % credentials.refresh_token)
            logging.info("Token expiry: %s" % credentials.token_expiry)

            try:
                credentials.refresh(http)
            except:
                logging.warning("Could not refresh Google API tokens for %s" % self)
                logging.warning("Refresh token: %s" % credentials.refresh_token)
                return

            self.save_credentials(credentials)

            logging.info("Access token: %s" % credentials.access_token)
            logging.info("Refresh token: %s" % credentials.refresh_token)
            logging.info("Token expiry: %s" % credentials.token_expiry)

        try: 
            http = credentials.authorize(http)
            return build(service_type, version, http=http)
        except:
            logging.error('Could not return Google Discovery APIs service object for User "%s"' % self)
            return

    def get_gd_client(self):
        """
        Returns client for Google Data APIs. Currently returns for Contacts API only
        Uses same google_credentials as get_service() for Gmail and newer Google APIs

        Args: 
            service_type: Default 'contacts'
        """
        try:
            credentials = OAuth2Credentials.new_from_json(self.google_credentials)
            auth2token = gdata.gauth.OAuth2TokenFromCredentials(credentials)
            gd_client = gdata.contacts.client.ContactsClient(source='<var>Ansatz/var>')
            gd_client = auth2token.authorize(gd_client)
            return gd_client
        except:
            logging.error('Could not return Google Data APIs client for User "%s"' % self)
            return

    def save_credentials(self, credentials):
        """
        Saves credentials as self.credentials while maintain refresh tokens. 

        Args:
            credentials: A oauth2.client.OAuth2Credentials object.
        """
        if not self.google_credentials or self.google_credentials is None:
            self.google_credentials = credentials.to_json()
        else:
            old_credentials = OAuth2Credentials.new_from_json(self.google_credentials)
            # Maintain refresh token if new credentials do not include one.
            # This arises when existing users log back in manually
            if old_credentials.refresh_token and not credentials.refresh_token:
                credentials.refresh_token = old_credentials.refresh_token

            logging.info("Saving refresh token: %s" % credentials.refresh_token)
            self.google_credentials = credentials.to_json()
        self.save()

    def get_refresh_token(self):
        return OAuth2Credentials.new_from_json(self.google_credentials).refresh_token


