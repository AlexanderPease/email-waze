import urllib
import json
from mongo import db
import pymongo, logging

"""
{
    "_id": {
        "$oid": "53175ad0fd6e45e48ff05200"
    },
    "tweet_template": "@[representative's account] voted [yes/no] on the Unfunded Mandates Information and Transparency Act of 2013. It passed and now goes to the Senate #FTV",
    "tweet": "Rep. Clark voted NO on the Unfunded Mandates Information and Transparency Act of 2013. It passed and now goes to the Senate #FTV",
    "datetime": {
        "$date": "2014-03-05T12:23:31.828Z"
    },
    "admin": "AlexanderMPease",
    "individual_votes": {
        "M000485": "Yea",
        "L000580": "Nay",
        "B000911": "Nay",
        "D000096": "Nay",
        "D000399": "Nay",
        ...etc
    },
    "vote": {
        "congress": "113",
        "source": "http://clerk.house.gov/evs/2014/roll090.xml",
        "url": "http://clerk.house.gov/evs/2014/roll090.xml",
        "fields": "voter_ids",
        "vote_type": "passage",
        "required": "1/2",
        "question": "On Passage -- H.R. 899 -- Unfunded Mandates Information and Transparency Act of 2013",
        "number": "90",
        "chamber": "house",
        "result": "Passed",
        "year": "2014",
        "voted_at": "2014-02-28T16:31:00Z",
        "roll_id": "h90-2014",
        "bill_id": "hr899-113",
        "roll_type": "On Passage"
    },
    "placeholders": {
        "choice_placeholder": "[yes/no]",
        "reps_account_placeholder": "@[representative's account]"
    },
    "tweeted": {
        "A000055": "YES",
        "B000013": "abstained",
        "B000213": "YES",
        "M001192": "YES",
        "A000367": "YES",
        "B001256": "YES",
        "B001282": "YES",
        "B001252": "YES",
        "B001242": "NO",
        "B001269": "YES",
        "B001279": "YES",
        "M000087": "NO",
        "A000369": "YES"
    }
}

"""

###########################
### Database methods
###########################

''' Returns all tweets, unless filtered '''
def find_all(spec=None, fields=None):
	return list(db.tweet.find(spec=spec, fields=fields, sort=[('datetime', pymongo.DESCENDING)]))

''' kwarg must be a dict '''
def find_one(kwarg):
    return db.tweet.find_one(kwarg)

''' Saves a tweet to the database.
    Must match entire vote dict to update vs. upsert '''
def save(t):
    if 'vote' in t.keys():
        return db.tweet.update({'vote':t['vote']}, t, upsert=True)
    elif 'tweet' in t.keys(): 
        return db.tweet.update({'tweet':t['tweet']}, t, upsert=True)
    else:
        raise Exception 

'''
def remove(intro):
  if 'id' in intro.keys():
    return db.brittbot.remove({'id':intro['id']})
'''



