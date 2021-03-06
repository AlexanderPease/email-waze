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
        return self.api_response(data={'result': 'hit test api'})


########################
### Returns email of self
### /api/currentuseremail
########################
class CurrentUserEmail(app.basic.BaseHandler):
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
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
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
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')

        if name or domain:
            results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
            if results:
                return self.api_response(data=results.to_json())

        return self.api_response(data=None)


########################
### ConnectionSearch
### /api/connectionsearch
########################
class ConnectionSearch(app.basic.BaseHandler):
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
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


########################
### ConnectionSearch
### /api/connectionbyemail
########################
class ConnectionByEmail(app.basic.BaseHandler):
    def get(self):
        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Query
        domain = self.get_argument('domain', '')
        cs = self.get_argument('cs', '') # defaults to ProfileConnectionSet
        if not domain:
            return self.api_error(400, 'No domain query given')
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
### /api/connectionbyemailforextension
########################
class ConnectionByEmailForExtension(app.basic.BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        """
        Returns dict with key-value pairs. All values are a single Connection 
        except for key 'domain' (ex: 'usv.com')
        """
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        domain = self.get_argument('domain', '')

        if not domain:
            return self.api_error(400, 'No domain query given')

        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Don't show connection to self
        if current_user.email == domain:
            return self.api_error(400, 'Queried self')

        # Setup needed to find results values
        results = {}
        group_users = current_user.all_group_users(include_self=False)
        try:
            profile = Profile.objects.get(email=domain)
            results['profile'] = profile.to_json()
        except:
            results = {'empty': True, 'email': domain}
            return self.api_response(results)

        # First two fields require exact profile
        if profile:
            # Last time current_user emailed profile
            try:
                connection = Connection.objects(profile=profile, user=current_user)
                results['current_user'] = connection[0].to_json()
            except:
                results['current_user'] = None

            # Last time a group_user emailed profile
            try:
                connections = Connection.objects(profile=profile, user__in=group_users).order_by("-latest_email_out_date")
                results['group_users_profile'] = connections[0].to_json()
            except:
                results['group_users_profile'] = None
        else:
            results['current_user'] = None
            results['group_users_profile'] = None

        # Final field is about domain
        if '@' in domain:
            domain = domain.split('@')[1] # doesn't include @
        results['domain'] = domain

        # Last time a group_user emailed domain of profile
        generic_domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'aol.com', 'comcast.net', 'outlook.com']
        if domain not in generic_domains:
            try:
                profiles = Profile.objects(email__icontains=domain)
                connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by("-latest_email_out_date")
                results['group_users_domain'] = connections[0].to_json()
            except:
                results['group_users_domain'] = None
        else:
            results['group_users_domain'] = None
            results['group_users_domain_generic'] = True

        # Return
        logging.info(results)
        if all(x == [] for x in results.itervalues()):
            return self.api_response(data=None)
        else:
            return self.api_response(data=results)


########################
### DomainConnections
### /api/domainconnections
########################
class DomainConnections(app.basic.BaseHandler):
    """
    Shows User's Connections (if any) to a particular domain (website). Easy
    to display Profiles that a User is connected to. 

    Returns:
        A dict containing a list of ProfileConnectionSets
    """
    def get(self):
        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        # Query
        domain = self.get_argument('domain', '')
        results = { 'domain': domain }
        if not domain:
            return self.api_error(400, 'No domain query given')
        profiles = Profile.objects(email__icontains=domain)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users)
        if connections and len(connections) > 0:
            pcs = ProfileConnectionSet.package_connections(connections)
            results['profile_connection_sets'] = connectionsets.list_to_json_list(pcs)
        else:
            results['profile_connection_sets'] = None
        return self.api_response(data=results)


########################
### GmailGetMessages
### /api/gmail/getmessages
########################
class GmailGetMessages(app.basic.BaseHandler):
    """
    Combines Gmail API method Users.messages.list and Users.messages.get so that
    it returns all the message objects that in a sanitized dictionary
    Args:
        email, if not the authenticated User's own email. Must have permission
        query, the Gmail query
    """
    def get(self):
        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')

        # Require query
        try:
            query = self.get_argument('query')
        except:
            return self.api_error(400, 'Query argument is required')

        # Determine gmail inbox to search
        user = self.get_argument('user', '')
        if user:
            # Currently only permissioned for Joel to access Fred's gmail account
            if self.current_user == 'joel@usv.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            elif self.current_user == 'me@alexanderpease.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            else:
                return self.api_error(400, 'Error in user argument')
        else:
            try:
                user = User.objects.get(email=self.current_user)
            except:
                return self.api_error(500, 'Could not find client user in database')

        gmail_service = user.get_service(service_type='gmail')
        if not gmail_service:
            return self.api_error(500, 'Could not instantiate authenticated service for %s' % user)
        messages = gmail.ListMessagesMatchingQuery(
            service = gmail_service,
            user_id = 'me',
            query   = query)
        data = []
        for message in messages:
            gmail_message = gmail.GetMessage(gmail_service, 'me', message['id'])
            gmail_dict = gmail.GetMessageHeader(gmail_message)
            body = gmail.GetMessageBody(gmail_message)
            gmail_dict['body'] = body
            data.append(gmail_dict)
        return self.api_response(data)

########################
### GmailListMessages
### /api/gmail/listmessages
########################
class GmailListMessages(app.basic.BaseHandler):
    """
    Pass through for Gmail API method Users.messages.list
    Args:
        email, if not the authenticated User's own email. Must have permission
        query, the Gmail query
    """
    def get(self):
        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')

        # Require query
        try:
            query = self.get_argument('query')
        except:
            return self.api_error(400, 'Query argument is required')

        # Determine gmail inbox to search
        user = self.get_argument('user', '')
        if user:
            # Currently only permissioned for Joel to access Fred's gmail account
            if self.current_user == 'joel@usv.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            elif self.current_user == 'me@alexanderpease.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            else:
                return self.api_error(400, 'Error in user argument')
        else:
            try:
                user = User.objects.get(email=self.current_user)
            except:
                return self.api_error(500, 'Could not find client user in database')

        gmail_service = user.get_service(service_type='gmail')
        if not gmail_service:
            return self.api_error(500, 'Could not instantiate authenticated service for %s' % user)
        messages = gmail.ListMessagesMatchingQuery(
            service = gmail_service,
            user_id = 'me',
            query   = query)
        return self.api_response(data=messages)

########################
### GmailGetMessage
### /api/gmail/getmessage
########################
class GmailGetMessage(app.basic.BaseHandler):
    """
    Pass through for Gmail API method Users.messages.get
    Args:
        email, if not the authenticated User's own email. Must have permission
        id, the Gmail ID of the message to retrieve
    """
    def get(self):
        # Authenticate user
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')

        # Require query
        try:
            gmail_id = self.get_argument('id')
        except:
            return self.api_error(400, 'Id argument is required')

        # Determine gmail inbox to search
        user = self.get_argument('user', '')
        if user:
            # Currently only permissioned for Joel to access Fred's gmail account
            if self.current_user == 'joel@usv.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            elif self.current_user == 'me@alexanderpease.com' and user == 'fred@usv.com':
                user = User.objects.get(email='fred@usv.com')
            else:
                return self.api_error(400, 'Error in user argument')
        else:
            try:
                user = User.objects.get(email=self.current_user)
            except:
                return self.api_error(500, 'Could not find client user in database')

        gmail_service = user.get_service(service_type='gmail')
        if not gmail_service:
            return self.api_error(500, 'Could not instantiate authenticated service for %s' % user)
        message = gmail.GetMessage(gmail_service, 'me', gmail_id)
        return self.api_response(data=message)


