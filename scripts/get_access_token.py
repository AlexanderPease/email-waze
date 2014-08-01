#!/usr/bin/env python
#
# Copyright 2007-2013 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# parse_qsl moved to urlparse module in v2.6
try:
    from urlparse import parse_qsl
except:
    from cgi import parse_qsl

import webbrowser
import oauth2 as oauth
import splinter

# For local usage
import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/ftv/followthevote')
    import settings
except:
    print 'could not import settings'

from db.mongo import db 

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

''' Twitter and twitter_password are for Splinter to log in with. Passing in both
    arguments triggers automatic flow. Without them, user is required to manually log in '''
def get_access_token(consumer_key, consumer_secret, twitter=None, twitter_password=None):
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_client = oauth.Client(oauth_consumer)

    print 'Requesting temp token from Twitter...'

    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'POST', body="oauth_callback=oob")

    if resp['status'] != '200':
        print 'Invalid respond from Twitter requesting temp token: %s' % resp['status']
    else:
        request_token = dict(parse_qsl(content))
        url = '%s?oauth_token=%s' % (AUTHORIZATION_URL, request_token['oauth_token'])

        print 'Requesting authorization from user...'
        print url

        if twitter and twitter_password:
            with splinter.Browser('chrome') as browser: # browser closes at end
                browser.visit(url)

                # Log in 
                browser.fill('session[username_or_email]', twitter)
                browser.fill('session[password]', twitter_password)
                browser.find_by_id('allow').first.click()
                
                # After click through, read pin_code
                pincode = browser.find_by_css('code').first.html
        else:    
            webbrowser.open(url) # Manually open browser
            pincode = raw_input('Pincode? ')

        token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(pincode)

        print 'Generating and signing request for an access token...'
        oauth_client = oauth.Client(oauth_consumer, token)
        resp, content = oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % pincode)
        access_token = dict(parse_qsl(content))

        if resp['status'] != '200':
            print 'The request for a Token did not succeed: %s' % resp['status']
            print resp
            print access_token
        else:
            print 'Access Token key: %s' % access_token['oauth_token']
            print 'Access Token secret: %s' % access_token['oauth_token_secret']
            return access_token['oauth_token'], access_token['oauth_token_secret']

def main():
    #access_key, access_secret = get_access_token(settings.get('twitter_consumer_key'), settings.get('twitter_consumer_secret')
    
    # OAuth all paid_twitter accounts 
    for a in list(db.paid_twitter.find()):
        # Only those without access keys
        if 'access_key' not in a.keys():
            access_key, access_secret = get_access_token(settings.get('twitter_consumer_key'), 
                settings.get('twitter_consumer_secret'), 
                twitter = a['twitter'],
                twitter_password = a['twitter_password'])
            a['access_key'] = access_key
            a['access_secret'] = access_secret
            db.paid_twitter.update({'twitter':a['twitter']}, a, upsert=True)



if __name__ == "__main__":
    main()




