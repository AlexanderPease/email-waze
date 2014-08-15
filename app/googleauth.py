import app.basic
import settings, logging, httplib2

from db.userdb import User
from oauth2client.client import OAuth2WebServerFlow

OAUTH_SCOPE = ('https://www.googleapis.com/auth/gmail.modify '
              'https://www.googleapis.com/auth/userinfo.email '
              'https://www.googleapis.com/auth/userinfo.profile') 
              #'https://www.googleapis.com/auth/plus.profile.emails.read '
              #'https://www.googleapis.com/auth/plus.me')

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
    flow = OAuth2WebServerFlow(client_id=settings.get('google_client_id'),
                           client_secret=settings.get('google_client_secret'),
                           scope=OAUTH_SCOPE,
                           redirect_uri='http://localhost:8001/auth/google/return', 
                           access_type='offline',
                           approval_prompt='force') # Needed for refresh tokens
    auth_uri = flow.step1_get_authorize_url()
    # Add cookies?
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
                           redirect_uri='http://localhost:8001/auth/google/return',
                           access_type='offline',
                           approval_prompt='force') # Needed for refresh tokens
    credentials = flow.step2_exchange(oauth_code)
    logging.info(credentials)
    if credentials is None or credentials.invalid:
      logging.warning('Credentials DNE or invalid')
      return self.redirect('/')
    
    # To get user's name and email address, build and query Google + service
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
      user.google_credentials = credentials.to_json()
      user.name = name
      user.email = email
      user.save()
      logging.info("Prexisting user %s is now logged in" % user.email)
    else:
      user = User(google_credentials=credentials.to_json(),
                  email=email,
                  name=name)
      user.save()
      logging.info('Saved new user %s' % user.email)

    return self.redirect('/')

    


    """ Twitter
    consumer_key = settings.get('twitter_consumer_key')
    consumer_secret = settings.get('twitter_consumer_secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, secure=True)
    auth.set_request_token(self.get_secure_cookie('request_token_key'), self.get_secure_cookie('request_token_secret'))
    auth.get_access_token(oauth_verifier)
    screen_name = auth.get_username()
    bounce_to = '/'

    access_token = {
      'secret': auth.access_token.secret,
      'user_id': '',
      'screen_name': '',
      'key': auth.access_token.key
    }

    # Do not log in and write to database if not a staff member
    if screen_name not in settings.get('staff'):
      return self.redirect(bounce_to)
    

    # If a staff member, go through sign-up/log-in flow
    # Check if we have this user already or not in the system
    user = userdb.get_user_by_screen_name(screen_name)
    print user
    if user:
      # set the cookies based on account details
      self.set_secure_cookie("user_id_str", user['user']['id_str'])
      self.set_secure_cookie("username", user['user']['screen_name'])
      bounce_to = '/admin'
      # OLD from usv app
      #if 'email_address' not in user or ('email_address' in user and user['email_address'] == ''):
        #bounce_to = '/user/%s/settings?1' % screen_name
    else:
      # need to create the account (so get more details from Twitter)
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret, secure=True)
      api = tweepy.API(auth)
      user = api.get_user(screen_name)
      access_token['user_id'] = user.id
      access_token['screen_name'] = user.screen_name
      user_data = {
        'auth_type': 'twitter',
        'id_str': user.id_str,
        'username': user.screen_name,
        'fullname': user.name,
        'screen_name': user.screen_name,
        'profile_image_url': user.profile_image_url,
        'profile_image_url_https': user.profile_image_url_https,
      }
      # now save to mongo
      userdb.create_new_user(user_data, access_token)
      # and set our cookies
      self.set_secure_cookie("user_id_str", user.id_str)
      self.set_secure_cookie("username", user.screen_name)
      bounce_to = '/admin'

    # let's save the screen_name to a cookie as well so we can use it for restricted bounces if need be
    self.set_secure_cookie('screen_name', screen_name, expires_days=30)

    return self.redirect(bounce_to)
    """



###########################
### LOG USER OUT OF ACCOUNT
### /auth/logout
###########################
class LogOut(app.basic.BaseHandler):
  def get(self):
    self.clear_all_cookies()
    self.redirect('/')
