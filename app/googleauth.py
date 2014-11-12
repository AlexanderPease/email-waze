import app.basic
import settings, logging, httplib2, datetime

from db.userdb import User
import tasks

from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from googleapiclient import errors

OAUTH_SCOPE = ('https://www.googleapis.com/auth/gmail.modify '
                'https://www.googleapis.com/auth/contacts.readonly '
                'https://www.googleapis.com/auth/userinfo.email ' #deprecated
                'https://www.googleapis.com/auth/userinfo.profile') #deprecated
                #'https://www.googleapis.com/auth/plus.profile.emails.read')
                #'https://www.googleapis.com/auth/plus.login')
                #'https://www.googleapis.com/auth/plus.me')
                

####################
### AUTH VIA GOOGLE
### /auth/google
####################
class Auth(app.basic.BaseHandler):
    def get(self):
        logging.info('Entered Auth')
        approval_prompt = self.get_argument('approval_prompt', '')
        logging.info(approval_prompt)
        if approval_prompt:
            # Manual request for refresh token is necessary
            # approval_prompt causes 'offline access' dialog box
            flow = OAuth2WebServerFlow(client_id=settings.get('google_client_id'),
                                client_secret=settings.get('google_client_secret'),
                                scope=OAUTH_SCOPE,
                                redirect_uri=redirect_uri(), 
                                access_type='offline', 
                                approval_prompt='force') 
        else:
            flow = OAuth2WebServerFlow(client_id=settings.get('google_client_id'),
                                client_secret=settings.get('google_client_secret'),
                                scope=OAUTH_SCOPE,
                                redirect_uri=redirect_uri(), 
                                access_type='offline')
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
                                access_type='offline')
                                # I thought this was needed for refresh tokens, 
                                # but if had been causing extra consent screen for 
                                # "offline consent"
                                #approval_prompt='force') 
        credentials = flow.step2_exchange(oauth_code)
        logging.info("Credentials: %s" % credentials)
        logging.info("Access token: %s" % credentials.access_token)
        logging.info("Refresh token: %s" % credentials.refresh_token)
        logging.info("Token expiry: %s" % credentials.token_expiry)
        if credentials is None or credentials.invalid:
            logging.warning('Credentials DNE or invalid')
            return self.redirect('/')
        
        # To get user's name and email address, build and query OAuth2 service
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('oauth2', 'v2', http=http)
        user_info = service.userinfo().get().execute()
        #print service.people().get(userId='me').execute()
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
            err = 'Log in failed. Google Auth did not return an email address'
            return self.redirect('/') # add err

        # Save credentials to user database
        try:
            user = User.objects.get(email__exact=email)
        except:
            user = None
        if user:
            # Update existing user info
            user.save_credentials(credentials)

            user.google_credentials_scope = OAUTH_SCOPE
            user.name = name
            user.email = email
            self.add_given_family_names(user, user_info)
            user.save()
            logging.info("Prexisting user %s is now logged in" % user.email)
        else:
            # Create and onboard new user
            user = User(google_credentials=credentials.to_json(),
                        google_credentials_scope=OAUTH_SCOPE,
                        email=email,
                        name=name,
                        joined=datetime.datetime.now())
            self.add_given_family_names(user, user_info)
            user.save()
            logging.info('Saved new user %s' % user.email)

        # If after saving user credentials the user still doesn't have a 
        # refresh_token, run /google/auth again with approval_prompt=force
        if not user.get_refresh_token():
            return self.redirect("/auth/google?approval_prompt=force")

            # On board new user to database
            if 'localhost' not in settings.get('base_url'):
                tasks.onboard_user.delay(user) # Celery task
            else:
                logging.info("Won't onboard new user in local")

        # Set cookies
        self.set_secure_cookie('user_email', user.email)
        self.set_secure_cookie('user_name', user.name)

        if not user.welcomed:
            return self.redirect('/user/welcome')
        else:
            return self.redirect('/')


    def add_given_family_names(self, user, user_info):
        if 'given_name' in user_info.keys():
            user.given_name = user_info['given_name']
        if 'family_name' in user_info.keys():
            user.family_name = user_info['family_name']


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

