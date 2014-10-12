import app.basic
import settings, logging, httplib2, datetime

from db.userdb import User
import tasks

OAUTH_SCOPE = ('https://www.googleapis.com/auth/gmail.modify '
                            'https://www.googleapis.com/auth/userinfo.email '
                            'https://www.googleapis.com/auth/userinfo.profile '
                            'https://www.googleapis.com/auth/contacts.readonly') 
                            #'https://www.googleapis.com/auth/plus.profile.emails.read '
                            #'https://www.googleapis.com/auth/plus.me')

from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from googleapiclient import errors

####################
### AUTH VIA GOOGLE
### /auth/google
####################
class Auth(app.basic.BaseHandler):
    def get(self):
        logging.info('Entered Auth')
        logging.info(settings.get('google_client_id'))
        logging.info(settings.get('google_client_secret'))
        flow = OAuth2WebServerFlow(client_id=settings.get('google_client_id'),
                                client_secret=settings.get('google_client_secret'),
                                scope=OAUTH_SCOPE,
                                redirect_uri=redirect_uri(), 
                                access_type='offline',
                                approval_prompt='force') # Needed for refresh tokens
        auth_uri = flow.step1_get_authorize_url()
        return self.redirect(auth_uri)

##############################
### RESPONSE FROM GOOGLE AUTH
### /auth/google/return
##############################
class AuthReturn(app.basic.BaseHandler):
    def get(self):
        logging.info('Entered AuthReturn')
        oauth_code = self.get_argument('code', '')

        flow = OAuth2WebServerFlow(client_id=settings.get('google_client_id'),
                                client_secret=settings.get('google_client_secret'),
                                scope=OAUTH_SCOPE,
                                redirect_uri=redirect_uri(),
                                access_type='offline',
                                approval_prompt='force') # Needed for refresh tokens
        credentials = flow.step2_exchange(oauth_code)
        logging.info(credentials)
        if credentials is None or credentials.invalid:
            logging.warning('Credentials DNE or invalid')
            return self.redirect('/')
        
        # To get user's name and email address, build and query OAuth2 service
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('oauth2', 'v2', http=http)
        user_info = service.userinfo().get().execute()
        """ 
        The above two lines can also be accomplished using GPlus API 
        service = build('plus', 'v1', http=http)
        user_info = service.people().get(userId='me').execute()
        """
        try:
            name = user_info['name']
            email = user_info['email']
        except:
            logging.info('No name or email for authenticating user')

        # Save credentials to user database
        try:
            user = User.objects.get(email__exact=email)
        except:
            user = None
        if user:
            # Update existing user info
            user.google_credentials = credentials.to_json()
            user.google_credentials_scope = OAUTH_SCOPE
            user.name = name
            user.email = email
            user.save()
            logging.info("Prexisting user %s is now logged in" % user.email)
        else:
            # Create and onboard new user
            user = User(google_credentials=credentials.to_json(),
                        google_credentials_scope=OAUTH_SCOPE,
                        email=email,
                        name=name,
                        joined=datetime.datetime.now())
            user.save()

            # On board new yser to database
            if settings.get('environment') in ['dev', 'prod']:
                tasks.onboard_user.delay(user) # Celery task
            else:
                logging.info("Won't onboard new user in local")

            logging.info('Saved new user %s' % user.email)

        # Set cookies
        self.set_secure_cookie('user_email', user.email)
        self.set_secure_cookie('user_name', user.name)

        return self.redirect('/')

###########################
### LOG USER OUT OF ACCOUNT
### /auth/logout
###########################
class LogOut(app.basic.BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect('/')


def redirect_uri():
    """
    Both Auth and AuthReturn need redirect_uri
    """
    if settings.get('environment') in ['dev', 'prod']:
        return '%s/auth/google/return' % settings.get('base_url')
    else:
        return 'http://localhost:8001/auth/google/return'

