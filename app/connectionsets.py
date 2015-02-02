import settings
import logging
import datetime
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from db.companydb import Company

class BaseProfileConnection:
    """
    Class for a Profile and relevant Connection info if it exists

    Args:
        profile is a Profile instance
        connections is a list of Connection instances
        self_connected is connection instance with current user
    """
    def __init__(self, profile, connections, current_user):
        self.profile_id = str(profile.id) ## .id is ObjectId
        self.name = profile.name
        self.email = profile.email
        self.burner = profile.burner
        self.connections = connections

        # The following fields are processed below
        self.company_name = None
        self.connection_strength = 0
        self.days_since_contact = 0
        self.total_emails_out = 0
        self.latest_email_out_date = None
        self.total_emails_in = 0
        self.latest_email_in_date = None
        self.self_connected = None

        # Get company name
        try:
            c = Company.objects.get(domain=profile.domain)
            self.company_name = c.name
        except:
            pass

        # Process connections and set other fields
        for c in self.connections:
            # emails_out
            if c.total_emails_out:
                self.total_emails_out += c.total_emails_out
            if c.latest_email_out_date:
                if not self.latest_email_out_date or self.latest_email_out_date > c.latest_email_out_date:
                    self.latest_email_out_date = c.latest_email_out_date
            # emails_in
            if c.total_emails_in:
                self.total_emails_in += c.total_emails_in
            if c.latest_email_in_date:
                if not self.latest_email_in_date or self.latest_email_in_date > c.latest_email_in_date:
                    self.latest_email_in_date = c.latest_email_in_date
            # self_connected
            if current_user:
                if current_user.same_user(c.user):
                    self.self_connected = c
        # days_since_contact
        if self.latest_email_date():
            self.days_since_contact = (datetime.datetime.now() - self.latest_email_date()).days
        # connection_strength
        if self.total_emails_out > 100 and self.days_since_contact < 90:
            self.connection_strength = 6
        elif self.total_emails_out > 25 and self.days_since_contact < 90:
            self.connection_strength = 5
        elif self.total_emails_out > 25 and self.days_since_contact < 180:
            self.connection_strength = 4
        elif self.total_emails_out > 10 and self.days_since_contact < 365:
            self.connection_strength = 3
        elif self.total_emails_out > 0 or self.total_emails_in > 0:
            self.connection_strength = 2
        else:
            self.connection_strength = 1

    def __repr__(self):
        return 'BaseProfileConnection: %s (%s)' % (self.name, self.email)

    # This is somewhat redundant with Profile.get_domain. But necessary b/c
    # BaseProfileConnection saves Profile fields, not Profile instance
    def get_domain(self):
        """
        Returns just the domain name of self.email
        Ex: reply.craigslist.com from foo@reply.craigslist.com
        """
        return self.email.split('@')[1]

    def total_emails(self):
        return self.total_emails_out + self.total_emails_in

    def to_json(self):
        '''
        Returns JSON dict of GroupConnectionSet instance
        '''
        json = {
            'profile_id': self.profile_id,
            'email': self.email, 
            'name': self.name, 
            'burner': self.burner,
            'total_emails_out': self.total_emails_out,
            'total_emails_in': self.total_emails_in,
            'connection_strength': self.connection_strength,
            'company_name': self.company_name
        }
        if self.connections:
            json['connections'] = []
            for c in self.connections:
                json['connections'].append(c.to_json())
        if self.self_connected:
            json['self_connected'] = self.self_connected.to_json()
        if self.latest_email_out_date:
            json['latest_email_out_date'] = self.latest_email_out_date_string()
        else:
            json['latest_email_out_date'] = None
        if self.latest_email_in_date:
            json['latest_email_in_date'] = self.latest_email_in_date_string()
        else:
            json['latest_email_in_date'] = None
        if self.days_since_contact:
            json['days_since_contact'] = self.days_since_contact
        else:
            json['days_since_contact'] = None
        return json

    def latest_email_out_date_string(self):
        if self.latest_email_out_date:
            return self.latest_email_out_date.strftime('%Y/%m/%d')
        elif self.total_emails_out:
            return 'Not found'
        else:
            return 'N/A'

    def latest_email_in_date_string(self):
        if self.latest_email_in_date:
            return self.latest_email_in_date.strftime('%Y/%m/%d')
        elif self.total_emails_in:
            return 'Not found'
        else:
            return 'N/A'

    def latest_email_date(self):
        """
        Returns more recent of latest_email_out/in_date, or None if neither exists
        """
        if not self.latest_email_out_date and not self.latest_email_in_date:
            return None
        elif not self.latest_email_out_date:
            return self.latest_email_in_date
        elif not self.latest_email_in_date:
            return self.latest_email_out_date
        elif self.latest_email_out_date > self.latest_email_in_date:
            return self.latest_email_out_date
        else:
            return self.latest_email_in_date

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

