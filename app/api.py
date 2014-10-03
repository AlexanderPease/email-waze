import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile
from db.userdb import User
import gmail


########################
### ProfileSearch
### /api/profilesearch
########################
class ProfileSearch(app.basic.BaseHandler):
    def get(self):
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')

        if name or domain:
            results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
            if results:
                return self.api_response(data=results.to_json())

        return self.api_response(data=None)


###########################
### API call for correspondence data from a single USVer
### /api/gmailinboxsearch
###########################
class GmailInboxSearch(app.basic.BaseHandler):
    def get(self):
        query = self.get_argument('q', '')
        user_email = self.get_argument('u','')
        if not query or not user_email:
            return self.api_error(400, 'Empty query')

        try:
            user = User.objects.get(email=user_email)
        except:
            logging.warning('API call for User of email %s failed' % user_email)
            return self.api_error(500, 'API call for User of email %s failed' % user_email)

        ### Ensure current user has access to user's contact book! 


        gmail_service = user.get_service(service_type='gmail')
        if gmail_service:
            # See if any messages match query
            emails_in = gmail.ListMessagesMatchingQuery(service=gmail_service, 
                                                        user_id='me', 
                                                        query= "from:" + query)
            emails_out = gmail.ListMessagesMatchingQuery(service=gmail_service, 
                                                        user_id='me', 
                                                        query= "to:" + query)
            if len(emails_in) > 0 or len(emails_out) > 0:
                results = {
                            'total_emails_in': len(emails_in),
                            'total_emails_out': len(emails_out)
                            }

                # Get dates of latest emails in and out
                latest_email_in = gmail.GetMessage(service=gmail_service, 
                                        user_id='me', 
                                        msg_id=emails_in[0]['id'])
                latest_email_out = gmail.GetMessage(service=gmail_service, 
                                        user_id='me', 
                                        msg_id=emails_out[0]['id'])

                latest_email_in_header = gmail.GetMessageHeader(latest_email_in)
                latest_email_out_header = gmail.GetMessageHeader(latest_email_out)

                if 'Date' in latest_email_in_header.keys():
                    results['latest_email_in_date'] = latest_email_in_header['Date']
                else:
                    results['latest_email_in_date'] = 'N/A'
                if 'Date' in latest_email_out_header.keys():
                    results['latest_email_out_date'] = latest_email_out_header['Date']
                else:
                    results['latest_email_in_date'] = 'N/A'

                return self.api_response(data=results)


        return self.api_response(data=None)

    ''' Simple query to the inbox, returns how many emails match query and the date of the latest email.
        Query must be a single string, i.e. not "science exchange" '''
    def search_mail(self, mail, query):
        if not query:
            query = "ALL"
        result, data = mail.search(None, query) # data is a list, but there is only data[0]. data[0] is a string of all the email ids for the given query. ex: ['1 2 4']
        ids = data[0] # ids is a space separated string containing all the ids of email messages
        id_list = ids.split() # id_list is an array of all the ids of email messages

        # Get date of latest email
        if id_list:
            latest_id = id_list[-1]
            result, data = mail.fetch(latest_id, "(RFC822)") # fetch the email body (RFC822) for the given ID
            raw_email = data[0][1] # raw_email is the body, i.e. the raw text of the whole email including headers and alternate payloads
            date = self.get_mail_date(raw_email)
        else:
            date = None
        return len(id_list), date

    ''' Login into an account '''
    def email_login(self, account, password):
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            result, message = mail.login(account, password)
            mail.select("[Gmail]/All Mail", readonly=True) #mark as unread
            if result != 'OK':
                raise Exception
            print 'Logged in as ' + account
            return mail
        except:
            print "Failed to log into " + account
            return None

    ''' Parses raw email and returns date sent. Picks out dates of the form "26 Aug 2013" '''
    def get_mail_date(self, raw_email):
        if raw_email:
            #Date: Mon, 5 Nov 2012 17:45:38 -0500
            date_string = re.search(r'[0-3]*[0-9] [A-Z][a-z][a-z] 20[0-9][0-9]', raw_email)
            if date_string:
                time_obj = time.strptime(date_string.group(), "%d %b %Y")
                return date(time_obj.tm_year, time_obj.tm_mon, time_obj.tm_mday)
            else:
                return None
        else:
            raise Exception




