import settings, logging
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection


class BaseProfileConnection:
    """
    Class for all Profiles and relevant Connection info if it exists

    Args:
        profile is a Profile instance
        connections is a list of Connection instances
        latest_email_out_date is a Connection instance with the most recent email out
    """
    def __init__(self, profile, connections=None, latest_email_out_date=None):
        self.name = profile.name
        self.email = profile.email
        self.burner = profile.burner
        self.connections = connections
        self.latest_email_out_date = latest_email_out_date

    def __repr__(self):
        return 'BaseProfileConnection: %s (%s)' % (self.name, self.email)

class GroupConnectionSet:
    """
    Class that groups Connections together by User
    """
    def __init__(self, email, name):
        self.email = email
        self.name = name
        self.connections = [] # start with empty array

    def __repr__(self):
        return 'GroupConnectionSet: %s (%s) connected to %s profiles' % (self.name, self.email, len(self.connections))

    def add_connection(self, c):
        self.connections.append(c)

    def to_json(self):
        '''
        Returns JSON dict of GroupConnectionSet instance
        '''
        json = {'email': self.email, 'name': self.name, 'connections': []}
        for c in self.connections:
            json['connections'].append(c.to_json())
        return json

    @classmethod
    def package_connections(self, connections):
        """
        Package and dedupe Connections for client-side use

        Args:
            connections are a list of Connections
        """
        results = []
        results_emails = [] # For fast indexing deduping connections
        for c in connections:
            try:
                existing_index = results_emails.index(c.user.email)
            except ValueError:
                existing_index = -1

            # If this connection is already in results, just add connection
            # to existing results 'profile'
            if existing_index != -1:
                results[existing_index].add_connection(c)
            # Else it is a new connection to add to results
            else:
                pc = GroupConnectionSet(c.user.email, c.user.name)
                pc.add_connection(c)
                results.append(pc)

                results_emails.append(c.user.email)
        return results

class ProfileConnectionSet:
    """
    Class that groups Connections together by Profile. 
    """
    def __init__(self, email, name):
        self.email = email
        self.name = name
        self.connections = [] # start with empty array

    def __repr__(self):
        return 'ProfileConnectionSet: %s (%s) connected to %s of your team members' % (self.name, self.email, len(self.connections))

    def add_connection(self, c):
        self.connections.append(c)

    def to_json(self):
        '''
        Returns JSON dict of GroupConnectionSet instance
        '''
        json = {'email': self.email, 'name': self.name, 'connections': []}
        for c in self.connections:
            json['connections'].append(c.to_json())
        return json

    @classmethod
    def package_connections(self, connections):
        """
        Package and dedupe Connections for client-side use

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
                results[existing_index].add_connection(c)
            # Else it is a new connection to add to results
            else:
                pc = ProfileConnectionSet(c.profile.email, c.profile.name)
                pc.add_connection(c)
                results.append(pc)

                results_emails.append(c.profile.email)

        return results

def list_to_json_list(l):
    """
    Turns list of either ProfileConnectionSets or GroupConnectionSets
    into a list of JSON ProfileConnectionSets or GroupConnectionSets
    """
    json_list = []
    for connection_set in l:
        json_list.append(connection_set.to_json())
    return json_list
