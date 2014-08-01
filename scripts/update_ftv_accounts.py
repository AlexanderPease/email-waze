''' Updates FTV twitter accounts of politicians'''
import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/ftv/followthevote')
    import settings
except:
    pass

from db.politiciandb import Politician

''' Updates all FTV Twitter accounts name, description, image, etc. 
	Make sure you want to update everything in this method before executing! '''
def update_all():
	for p in Politician.objects(twitter='RepKarenBass'):
		print "Updating %s..." % p.name()
		try:
			api = p.login_twitter()
		except:
			print "Could not authenticate with %s" % p.name()
			break
		
		# Determine description, name, location, and url...
		if p.twitter:
			p.ftv.description = 'Tweeting the Congressional votes of @%s' % p.twitter # 160 char max
		else:
			p.ftv.description = 'Tweeting the Congressional votes of %s' % p.brief_name()
		
		p.ftv.name = 'FTV for %s' % p.brief_name() # 20 char max
		if len(p.ftv.name) > 20:
			p.ftv.name = p.ftv.name.replace('.', '')
			if len(p.ftv.name) > 20:
				p.ftv.name = "FTV @%s" % p.twitter
				if len(p.ftv.name) > 20:
					print p['ftv']['name']
					print len(p['ftv']['name'])
					raise Exception

		# ...and write
		try:
			api.update_profile(name=p.ftv.name, 
							location='Washington, D.C.', 
							description=p.ftv.description,
							url='http://followthevote.org')
			profile_img_path = settings.get('project_root') + '/static/img/congress.jpeg'
			api.update_profile_image(profile_img_path)
			background_img_path = settings.get('project_root') + '/static/img/congress.jpeg'
			api.update_profile_background_image(background_img_path, tile='true') # Not working
			p.save
		except:
			print "Could not update %s" % p.name()


''' Make every FTV account follow every other FTV account '''
def update_all_friends():
	fail_list = []
	for p in Politician.objects(): #__raw__={'ftv':{'$exists':True}}):
		print "Updating friends of %s..." % p.name()
		try:
			api = p.login_twitter()
		except:
			print "Could not authenticate with %s" % p.name()
			break

		list_friends = api.friends_ids()

		for p2 in Politician.objects(): #__raw__={'ftv':{'$exists':True}}):
			if not p.bioguide_id == p2.bioguide_id and p2.ftv.twitter_id not in list_friends and p2.ftv.twitter not in fail_list:
				try:
					api.create_friendship(p2.ftv.twitter_id)
					print "Following %s..." % p2.ftv.twitter
				except:
					print p2.ftv.twitter
					print p2.ftv.twitter_id
					fail_list.append(p2.ftv.twitter)
		print fail_list

''' Pulls actual p.ftv info from Twitter (except email) so that
	database is completely accurate '''
def check_twitter_ftv():
	fail_list = []
	for p in Politician.objects(twitter="RepKarenBass"):
		print "Checking %s..." % p.name()
		try:
			api = p.login_twitter()
		except:
			print "Failed: %s" % p.name()
			fail_list.append(p.bioguide_id)
		me = api.verify_credentials()
		p.ftv.twitter = me.screen_name
		p.ftv.description = me.description
		p.ftv.name = me.name
		p.save()
	if fail_list:
		print fail_list

def main():
	update_all()
	#update_all_friends()
	check_twitter_ftv()

if  __name__ =='__main__':main()


'''OLD
# Using tweepy
def update_all_ftv2():
	for p in politiciandb.find_all_with_ftv():
		print "Updating %s..." % p['name']
		api = politiciandb.login_tweepy(p)

		profile_img_path = settings.get('project_root') + '/static/img/congress.jpeg'
		api.update_profile_image(profile_img_path)
		background_img_path = settings.get('project_root') + '/static/img/congress.jpeg'
		api.update_profile_background_image(background_img_path, tile='true') # Not working

def update_all_ftv():
	for p in politiciandb.find_all_with_ftv():
		print "Updating %s..." % p['name']
		api = politiciandb.login_twitter(p)
		
		# Get all twitter ids and save to database
		user = api.VerifyCredentials()
		p['ftv']['id'] = user.id
		politiciandb.save(p)

		# Set description, name, location, and url...
		if 'twitter' in p.keys():
			p['ftv']['description'] = 'Tweeting the Congressional votes of %s' % p['twitter'] # 160 char max
			if len(p['ftv']['description']) > 160:
				print len(p['ftv']['name'])
				raise Exception
		else:
			p['ftv']['description'] = 'Tweeting the Congressional votes of %s' % p['brief_name'] # 160 char max
			if len(p['ftv']['description']) > 160:
				print len(p['ftv']['name'])
				raise Exception
		
		p['ftv']['name'] = 'FTV for %s' % p['brief_name'] # 20 char max
		if len(p['ftv']['name']) > 20:
			p['ftv']['name'] = p['ftv']['name'].replace('.', '')
			if len(p['ftv']['name']) > 20:
				p['ftv']['name'] = "FTV @%s" % p['twitter_id']
				if len(p['ftv']['name']) > 20:
					print p['ftv']['name']
					print len(p['ftv']['name'])
					raise Exception

		# ...and write
		api.UpdateProfile(name=p['ftv']['name'], 
						location='Washington, D.C.', 
						description=p['ftv']['description'],
						profileURL='http://followthevote.org')
		politiciandb.save(p)

		# Set profile image and background image
		# TODO

		# Potentially change screen_name, if needed


		# Make every FTV account follow every other FTV account
		for p2 in politiciandb.find_all_with_ftv():
			if not p == p2:
				politiciandb.add_friend(p, p2)



# Update @FollowTheVote
def update_ftv_twitter():
	api = python_twitter.Api(consumer_key=settings.get('twitter_consumer_key'),
                consumer_secret=settings.get('twitter_consumer_secret'),
                access_token_key=settings.get('ftv_twitter_consumer_key'),
                access_token_secret=settings.get('ftv_twitter_consumer_secret'))
	
	# Make @FollowTheVote follow all FTV and politician accounts
	for p in politiciandb.find_all():
		if 'twitter_id' in p.keys():
			if not api.LookupFriendship(screen_name=p['twitter_id']):
				try:
					api.CreateFriendship(screen_name=p['twitter_id'])
				except:
					print "Failed to add politician's twitter: %s" % p['twitter_id']
		if 'ftv' in p.keys():
			if not api.LookupFriendship(screen_name=p['twitter_id']):
				try:
					api.CreateFriendship(screen_name=p['ftv']['twitter'])
				except:
					print "Failed to add FTV twitter: %s " % p['ftv']['twitter']
'''
