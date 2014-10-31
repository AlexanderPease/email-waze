from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection

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
    Class that groups Connections together by User
    """
    def __init__(self, email, name):
        self.email = email
        self.name = name
        self.connections = [] # start with empty array

    def __repr__(self):
        return 'ProfileConnectionSet: %s (%s) connected to %s of your team members' % (self.name, self.email, len(self.connections))

    def add_connection(self, c):
        self.connections.append(c)


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
