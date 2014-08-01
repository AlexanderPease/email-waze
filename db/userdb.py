from mongo import db

# For update_twitter
import tweepy
import settings
import urllib2

"""
{
  'user': { 
    'id_str':'', 
    'auth_type': '', 
    'username': '', 
    'fullname': '', 
    'screen_name': '', 
    'profile_image_url_https': '', 
    'profile_image_url': '', 
    'is_blacklisted': False 
    },
  'access_token': { 'secret': '', 'user_id': '', 'screen_name': '', 'key': '' },
  'email_address': '',
  'role': '',
  'tags':[],
  "disqus_token_type": "Bearer",
  "disqus_access_token": "",
  "disqus_expires_in": 0,
  "disqus_refresh_token": "",
  "disqus_username": "",
  "disqus_user_id": 0,
  'yammer' {
    'access_token': {
      'token'
    }
    lots of other stuff
  }
  'in_usvnetwork': False
}

"""

''' Returns all users '''
def find_all():
  return db.user_info.find()

def get_user_by_id_str(id_str):
  return db.user_info.find_one({'user.id_str': id_str})

def get_user_by_screen_name(screen_name):
  return db.user_info.find_one({'user.screen_name': screen_name})

def get_user_by_email(email_address):
  return db.user_info.find_one({'email_address':email_address})
  
def get_disqus_users():
  return db.user_info.find({'disqus': { '$exists': 'true' }})
  
def get_newsletter_recipients():
  return list(db.user_info.find({'wants_daily_email': True}))

def create_new_user(user, access_token):
  print 'create new user'
  return db.user_info.update({'user.id_str': user['id_str']}, {'user':user, 'access_token':access_token, 'email_address':'', 'role':''}, upsert=True)

def save_user(user):
  print 'save user'
  return db.user_info.update({'user.id_str': user['user']['id_str']}, user)

def get_user_count():
  return db.user_info.count()

