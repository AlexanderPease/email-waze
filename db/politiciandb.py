import settings
from mongoengine import *
import tweepy, logging

mongo_database = settings.get('mongo_database')
connect('politician', host=mongo_database['host'])

class FTV(EmbeddedDocument):
	twitter = StringField(required=True, unique=True)
	twitter_id = IntField(required=True, unique=True)
	twitter_password = StringField(required=True)
	access_key = StringField(required=True)
	access_secret = StringField(required=True)
	name = StringField(max_length=20)
	description = StringField(max_length=160)

	email = StringField()
	email_password = StringField() 

class Politician(Document):
	first_name = StringField(required=True)
	last_name = StringField(required=True)
	title = StringField(required=True)
	district = IntField(required=False) # Senators don't have (but they could have Jr/Sr)
	state = StringField(required=True, max_length=2)
	full_state_name = StringField(required=True)
	party = StringField(required=True, max_length=1)
	chamber = StringField(required=True)

	portrait_path = StringField(required=True)
	twitter = StringField(required=False, max_length=16) # Politician's personal twitter, most have one
	bioguide_id = StringField(required=True, unique=True)

	ftv = EmbeddedDocumentField("FTV", required=False)

	def __str__(self):
		return self.name()

	def name(self):
		return self.title + ". " + self.first_name + " " + self.last_name

	def brief_name(self):
		return self.title + ". " + self.last_name

	''' Log in using tweepy '''
	def login_twitter(self):
		try:
		    auth = tweepy.OAuthHandler(settings.get('twitter_consumer_key'), settings.get('twitter_consumer_secret'))
		    auth.set_access_token(self.ftv.access_key, self.ftv.access_secret)
		    return tweepy.API(auth)
		except:
		    if self.ftv:
		      print "@%s's account %s failed to authenticate with API" % (self.brief_name, self.ftv.twitter)
		      raise Exception
		    else: 
		      #print '@%s does not have an FTV account' % p['brief_name']
		      return None

	''' Actually tweet from their FTV account! 
	    Returns True if successfully tweeted, False if failed '''
	def tweet(self, t, api=None):
	  logging.info('entered tweet()')
	  if len(t) > 140:
	  	logging.info('Tweet too long!!')
	  	t = t[0:140]
	  if not api:
	  	api = self.login_twitter()
	  if api:
	    try:
	      status = api.update_status(t)
	      logging.info('@%s posted status:' % self.ftv.twitter)
	      return_flag = True
	    except:
	      logging.info('@%s FAILED to post status:' % self.ftv.twitter)
	      return_flag = False

	    # Log status for debugging
	    try:
	    	logging.info(t)
	    except:
	    	logging.info('Could not log tweet to console, must be encoding error')

	    logging.info('leaving tweet()')
	    return return_flag

	


	


