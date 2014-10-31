import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile
from db.userdb import User
from db.groupdb import Group
from db.connectiondb import Connection
from mongoengine.queryset import Q
import api


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    name = self.get_argument('name', '')
    domain = self.get_argument('domain', '')

    
    if name or domain:
        # Global profile results
        profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

        # Connections
        current_user = User.objects.get(email=self.current_user)
        group_users = current_user.all_group_users()
        connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by('-total_emails_out')

        # De-dupe profiles that user is connected to
        # This is djanky because can't do joins :(
        ps = []
        for p in profiles:
            p_flag = True
            for c in connections:
                if p.id == c.profile.id:
                    p_flag = False
            if p_flag:
                ps.append(p)
        profiles = ps

        # Organize connections into dictionaries to handle multiple people being
        # connected to the same email
        superconnections = SuperConnection.package_connections(connections)
        logging.info(connections)

        return self.render('public/index.html', 
            profiles=profiles, 
            connections=connections, 
            superconnections=superconnections, 
            email_obscure=Profile.get_domain)
    else:
        return self.render('public/index.html', profiles=None, connections=None)


class About(app.basic.BaseHandler):
  def get(self):
    return self.render('public/about.html')


class SuperConnection:
    def __init__(self, email, name):
        self.email = email
        self.name = name
        self.connections = [] # start with empty array

    def __str__(self):
        return 

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
                pc = SuperConnection(c.profile.email, c.profile.name)
                pc.add_connection(c)
                results.append(pc)

                results_emails.append(c.profile.email)

        return results

