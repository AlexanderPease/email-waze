
''' Updates FTV twitter accounts of politicians'''
import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/ftv/followthevote')
    import settings
except:
    pass

from db.politiciandb import Politician
import splinter
import time

''' Updates all FTV account usernames '''
def update_accounts():
	fail_list = [] # Those accounts that failed to update
	for p in Politician.objects(title="Sen"):
		# Calc new username
		if p.title == 'Sen':
			if p.ftv.twitter == 'FTV_' + p.state + '_Senator1' or p.ftv.twitter == 'FTV_' + p.state + '_Senator2':
				new_username = p.ftv.twitter
				if p.ftv.email == p.state + "Sen1@followthevote.org" or p.ftv.email == p.state + "Sen2@followthevote.org": 
					new_email = p.ftv.email
				else:
					if '1' in new_username:	
						new_email = p.state + "Sen1@followthevote.org" 
					else:
						new_email = p.state + "Sen2@followthevote.org"
			else:
				# then need a new username
				new_username = 'FTV_' + p.state + '_Senator1'
				if Politician.objects(ftv__twitter=new_username, bioguide_id__ne=p.bioguide_id):
					new_username = 'FTV_' + p.state + '_Senator2'
				
				if '1' in new_username:	
					new_email = p.state + "Sen1@followthevote.org" 
				else:
					new_email = p.state + "Sen2@followthevote.org"
		elif p.title == 'Rep':
			new_username = 'FTV_' + p.state + str(p.district)
			new_email = p.state + str(p.district) + "@followthevote.org"
		else:
			if len(p.full_state_name) <= 11:
				new_username = 'FTV_' + p.full_state_name 
			else:
				new_username = 'FTV_' + p.state
			new_email = p.state + "@followthevote.org"

		# Run splinter log in only if username needs updating
		if new_username != p.ftv.twitter: # or new_email != p.ftv.email:
			print 'Changing %s...' % p.name()
			print "new: " + new_username
			print p.ftv.twitter
			print ""
			print "new: " + new_email
			print p.ftv.email
			print ""
			try: 
				with splinter.Browser('chrome') as browser: # browser closes at end
					browser.visit('https://twitter.com')

					# Log in 
					browser.fill('session[username_or_email]', p.ftv.twitter)
					browser.fill('session[password]', p.ftv.twitter_password)
					browser.find_by_css('button').first.click()

					# Click on settings gear icon
					browser.visit('https://twitter.com/settings/account')

					# Change username and/or email
					if new_username != p.ftv.twitter:
						browser.fill('user[screen_name]', new_username)
					#if new_email != p.ftv.email:
					browser.fill('user[email]', new_email)
					time.sleep(1)
					browser.find_by_id('settings_save').first.click()
					time.sleep(1)
					browser.fill('auth_password', p.ftv.twitter_password)
					browser.find_by_id('save_password').first.click()

					# Save to database
					p.ftv.twitter = new_username
					old_email = p.ftv.email
					p.ftv.email = new_email
					p.ftv.email_password = ""
					p.save()
					print 'Saved!'
					print "-------------"

					# Click on email confirmation
					if new_email != old_email:
						time.sleep(3) # Wait for confirmation email to arrive
						#gmail_confirm(browser) code below instead
						browser.visit('https://gmail.com')

						# Log in 
						browser.fill('Email', 'admin@followthevote.org')
						browser.fill('Passwd', 'statueofliberty')
						browser.find_by_id('signIn').first.click()

						# Click on first email
						browser.find_by_css('td')[7].click()
						
						# Click on link to verify email
						browser.find_link_by_partial_href('https://twitter.com')[3].click() #says this link is invalid but still seems to work
				
			except:
				fail_list.append(p.name())
	print fail_list

			
''' Opens first email in admin@followthevote.org and clicks on confirmation link
	This should be called immediately upon sending confirmation link '''			
def gmail_confirm(browser):
	browser.visit('https://gmail.com')

	# Log in 
	browser.fill('Email', 'admin@followthevote.org')
	browser.fill('Passwd', 'statueofliberty')
	browser.find_by_id('signIn').first.click()

	# Click on first email
	browser.find_by_css('td')[7].click()
	
	# Click on link to verify email
	browser.find_link_by_partial_href('https://twitter.com')[3].click() #says this link is invalid but still seems to work
	'''	
	twitter_links = browser.find_link_by_partial_href('https://twitter.com')
	for l in twitter_links:
		try:
			l.click()
			print 'success'
		except:
			print 'fail'
	#browser.find_link_by_partial_href('https://twitter.com/i/redirect').first.click()
	'''
	time.sleep(5)


def main():
    #with splinter.Browser('chrome') as browser:
    # 	gmail_confirm(browser)
    update_accounts()

if  __name__ =='__main__':main()

