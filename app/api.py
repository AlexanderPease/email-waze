import app.basic, settings, ui_methods, tornado.web
import logging
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
from connectionsets import GroupConnectionSet, ProfileConnectionSet
import connectionsets
import gmail

########################
### ProfileSearch
### /api/test
########################
class Test(app.basic.BaseHandler):
    def get(self):
        logging.info(self.current_user)
        logging.info('HIT TEST API!!!!!!!!!!!')
        return self.api_response(data=None)


########################
### Returns email of self
### /api/currentuseremail
########################
class CurrentUserEmail(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        return current_user.email


########################
### Profile
### /api/profilebyemail
########################
class ProfileByEmail(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        domain = self.get_argument('domain', '')
        try:
            p = Profile.objects.get(email=domain)
            return self.api_response(data=p.to_json())
        except:
            return self.api_response(data=None)


########################
### ProfileSearch
### /api/profilesearch
########################
class ProfileSearch(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')

        if name or domain:
            results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
            if results:
                return self.api_response(data=results.to_json())

        return self.api_response(data=None)


########################
### ConnectionSearch
### /api/connectionbyemail
########################
class ConnectionByEmail(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        domain = self.get_argument('domain', '')
        cs = self.get_argument('cs', '') # defaults to ProfileConnectionSet

        if not domain:
            return self.api_error(400, 'No domain query given')

        # Authenticate user
        logging.info(self.current_user)
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Don't show connection to self
        if current_user.email == domain:
            return self.api_error(400, 'Queried self')

        try:
            profile = Profile.objects.get(email=domain)
        except:
            return self.api_response(data=None)

        group_users = current_user.all_group_users()
        connections = Connection.objects(profile=profile, user__in=group_users)
        if connections and len(connections) > 0:
            if cs == 'group':
                results = GroupConnectionSet.package_connections(connections)
            else:
                results = ProfileConnectionSet.package_connections(connections)
            results = connectionsets.list_to_json_list(results)

            # Should only be one result
            if len(results) > 1 or len(results) == 0:
                return self.api_error(500, 'Multiple Connections after deduping by email')

            return self.api_response(data=results[0]) # Return single Connection

        return self.api_response(data=None)


########################
### ConnectionSearch
### /api/connectionsearch
########################
class ConnectionSearch(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')
        cs = self.get_argument('cs', '') # defaults to ProfileConnectionSet

        if name or domain:
            try:
                current_user = User.objects.get(email=self.current_user)
            except:
                return self.api_error(500, 'Could not find client user in database')

            profiles = Profile.objects(name__icontains=name, email__icontains=domain)

            # insert limits on how many profiles this returns?

            group_users = current_user.all_group_users()
            connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by('-latest_email_out_date')

            if connections and len(connections) > 0:
                if cs == 'group':
                    results = GroupConnectionSet.package_connections(connections)
                else:
                    results = ProfileConnectionSet.package_connections(connections)
                results = connectionsets.list_to_json_list(results)

                return self.api_response(data=results)

        return self.api_response(data=None)

'''
def PackageConnections(connections):
    """
    Package and dedupe connections for client-side use

    Args:
        connections are a list of Connections
    """
    results = []
    results_emails = [] # For fast indexing deduping connections
    for c in connections:
        try:
            existing_index = results_emails.index(c.profile.email)
        except ValueError:
            existing_index = -1

        # If this connection is already in results, just add connection
        # to existing results 'profile'
        if existing_index != -1:
            results[existing_index]['connections'].append({'connected_user_name': c.user.name,
                                            'connected_user_email': c.user.email,
                                            'total_emails_in': c.total_emails_in,
                                            'latest_email_in_date': c.latest_email_in_date_string(),
                                            'total_emails_out': c.total_emails_out,
                                            'latest_email_out_date': c.latest_email_out_date_string()})
        # Else it is a new connection to add to results
        else:
            results.append({'email': c.profile.email,
                            'name': c.profile.name,
                            'connections':[{'connected_user_name': c.user.name,
                                            'connected_user_email': c.user.email,
                                            'total_emails_in': c.total_emails_in,
                                            'latest_email_in_date': c.latest_email_in_date_string(),
                                            'total_emails_out': c.total_emails_out,
                                            'latest_email_out_date': c.latest_email_out_date_string()
                                            }]
                            })
            results_emails.append(c.profile.email)

    return results
'''

###########################
### API call for correspondence data from a single USVer
### This literally searches the Gmail inbox, not the Ansatz database
### /api/gmailinboxsearch
###########################
"""
class GmailInboxSearch(app.basic.BaseHandler):
    def get(self):
        query = self.get_argument('q', '')
        #user_email = self.get_argument('u','')
        user_email = 'alexander@usv.com' ### HACK
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
"""


