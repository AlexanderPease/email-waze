import app.basic, settings, ui_methods, tornado.web
import logging
import api


########################
### Profile
### /api/1.0/profilebyemail
########################
class ProfileByEmail(app.basic.BaseHandler):
    def get(self):
        logging.info('new profilebyemail')


########################
### ProfileSearch
### /api/1.0/profilesearch
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
### DomainConnections
### /api/1.0/domainconnections
########################
class DomainConnections(app.basic.BaseHandler):
    """
    Shows User's Connections (if any) to a particular domain (website). Easy
    to display Profiles that a User is connected to. 

    Returns:
        A list of ProfileConnectionSets
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
        if not domain:
            return self.api_error(400, 'No domain query given')
        profiles = Profile.objects(email__icontains=domain)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users)
        if connections and len(connections) > 0:
            results = ProfileConnectionSet.package_connections(connections)
            results = connectionsets.list_to_json_list(results)
            return self.api_response(data=results)

        return self.api_response(data=None)

########################
### ConnectionSearch
### /api/connectionsearch
########################
class ConnectionSearch(app.basic.BaseHandler):
    #@tornado.web.authenticated
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
### ConnectionEmail
### /api/1.0/connectionbyemail
########################
class ConnectionByEmail(app.basic.BaseHandler):
    #@tornado.web.authenticated
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
### /api/1.0/connectionbyemailforextension
########################
class ConnectionByEmailForExtension(app.basic.BaseHandler):
    def get(self):
        pass

