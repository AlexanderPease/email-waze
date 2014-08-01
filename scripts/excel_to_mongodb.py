import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/ftv/followthevote')
    import settings
except:
    print 'Could not import settings.py'

import csv
from db.mongo import db
from db.politiciandb import Politician, FTV
from db.old import politiciandb
import tweepy


def save(doc):
	return db.paid_twitter.update({'twitter':doc['twitter']}, doc, upsert=True)

''' Writes account info from excel into a mongodb collection '''
def excel_to_mongodb(filename):
    with open(filename, 'U') as f:
        reader = csv.reader(f, dialect=csv.excel_tab)
        for row_list in reader:
            row_string = row_list[0]
            row = row_string.split(',')
            doc = {'name': row[0],
            	'twitter': row[1],
            	'twitter_password': row[2],
            	'email': row[4],
            	'email_password': row[5]}
            save(doc)


''' Adds twitter accounts to politicians without an FTV account 
	There's something a bit wrong with the counters here '''
def add_twitter_to_politician():
	# Politicians w/out FTV
	ps = Politician.objects(ftv__exists=False)
	p_counter = 0
	print len(ps)

	for a in db.paid_twitter.find():
		if 'assigned_to_bioguide_id' not in a.keys():
			if p_counter < len(ps): # Don't go over array length
				p = ps[p_counter]
				print p_counter

				print p.last_name
				# Double check p.ftv doesn't exist
				if p.ftv:
					raise Exception

				# Assign new twitter account!
				p.ftv = FTV(twitter = a['twitter'],
							twitter_id = a['twitter_id'],
							access_key = a['access_key'],
							access_secret = a['access_secret'],
							name = a['name'],
							email = a['email'],
							email_password = a['email_password'])
				p.save()
				p_counter = p_counter + 1
				a['assigned_to_bioguide_id'] = p.bioguide_id
				save(a)

			else:
				print "No more politicians! We have extra twitter accounts!"

def get_twitter_ids():
	for a in db.paid_twitter.find():
		if 'twitter_id' not in a.keys():
			auth = tweepy.OAuthHandler(settings.get('twitter_consumer_key'), settings.get('twitter_consumer_secret'))
			auth.set_access_token(a['access_key'], a['access_secret'])
			api = tweepy.API(auth)
			creds = api.verify_credentials() 
			a['twitter_id'] = creds.id
			save(a)
		

def main():
    #excel_to_mongodb('../paid_accounts/500 Twitter Accounts_Alexander Pease.csv')

    # Get access tokens before adding to politicians
    #get_twitter_ids()
    #add_twitter_to_politician()


if __name__ == "__main__":
    main()
