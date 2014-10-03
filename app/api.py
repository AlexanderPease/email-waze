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
        #user_email = self.get_argument('u','')
        user_email = 'alexander@usv.com'
        if not query or not user_email:
            return self.api_error(400, 'Empty query')

        try:
            user = User.objects.get(email=user_email)
        except:
            logging.warning('API call for User of email %s failed' % user_email)
            return self.api_error(500, 'API call for User of email %s failed' % user_email)

        ### TODO!!!
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
                            'name': user.name,
                            'email': user.email,
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



