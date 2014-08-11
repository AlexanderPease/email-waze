import os
import time
import tornado.options

# Environmenal settings for heroku#
# If you are developing for heroku and want to set your settings as environmental vars
# create settings_local_environ.py in the root folder and use:
# os.environ['KEY'] = 'value'
# to simulate using heroku config vars
# this is better than using a .env file and foreman
# since it still allows you to see logging.info() output.
# Make sure to also put import os in this settings_local_environ.py
try:
  import settings_local_environ
except:
  pass
  
time.tzset()

tornado.options.define("environment", default="dev", help="environment")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))

options = {
  'dev' : {
    'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 'port' : 27017, 'db' : os.environ.get('DB_NAME')},
    'base_url' : os.environ.get('BASE_URL'),
  },
  'test' : {
    'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 'port' : 27017, 'db' : os.environ.get('DB_NAME')},
    'base_url' : os.environ.get('BASE_URL'),
  },
  'prod' : {
    'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 'port' : 27017, 'db' : os.environ.get('DB_NAME')},
    'base_url' : 'www.usv.com',
  },
  'production' : {
    'mongo_database' : {'host' : os.environ.get('MONGODB_URL'), 'port' : 27017, 'db' : os.environ.get('DB_NAME')},
    'base_url' : 'www.usv.com',
  }
}

default_options = {
  'project_root': os.path.abspath(os.path.join(os.path.dirname(__file__))),

  # twitter details
  'twitter_consumer_key': os.environ.get("TWITTER_CONSUMER_KEY"),
  'twitter_consumer_secret': os.environ.get("TWITTER_CONSUMER_SECRET"),

  # @FollowTheVote
  'ftv_twitter_handle': os.environ.get("FTV_TWITTER_HANDLE"),
  'ftv_twitter_consumer_key': os.environ.get('FTV_TWITTER_CONSUMER_KEY'),
  'ftv_twitter_consumer_secret': os.environ.get('FTV_TWITTER_CONSUMER_SECRET'),

  # disqus details
  'disqus_public_key': '',
  'disqus_secret_key': '',
  'disqus_short_code': '',

  # postmark details
  'sendgrid_user': os.environ.get("SENDGRID_USER"),
  'sendgrid_secret': os.environ.get("SENDGRID_SECRET"),

  'staff':[
    "AlexanderPease",
  ],

  # define the various roles and what capabilities they support
  'staff_capabilities': [
    'connect_to_yammer',
    'send_daily_email',
    'see_admin_link',
    'delete_users',
    'delete_posts',
    'post_rich_media',
    'feature_posts',
    'edit_posts',
    'super_upvote',
    'super_downvote',
    'downvote_posts',
    'manage_disqus'
  ],
  'user_capabilities': [], 
  
  'module_dir': os.path.join(PROJECT_ROOT, 'templates/modules') #delete!
}

def get(key):
  # check for an environmental variable (used w Heroku) first
  if os.environ.get('ENVIRONMENT'):
    env = os.environ.get('ENVIRONMENT')
  else:
    env = tornado.options.options.environment

  if env not in options:
    raise Exception("Invalid Environment (%s)" % env)

  if key == 'environment':
    return env

  v = options.get(env).get(key) or os.environ.get(key.upper()) or default_options.get(key)

  if callable(v):
    return v

  if v is not None:
    return v

  return default_options.get(key)
