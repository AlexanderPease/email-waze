import app.basic, settings, ui_methods, tornado.web
import logging
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
from connectionsets import GroupConnectionSet
from connectionsets import ProfileConnectionSet
from connectionsets import BaseProfileConnection
from connectionsets import list_to_json_list
import math

RESULTS_PER_PAGE = 20

########################
### SearchBaseConnectionSet
### /api/searchbaseprofileconnection
########################
class SearchBaseProfileConnection(app.basic.BaseHandler):
    def get(self):
        if not self.current_user:
            return self.api_error(401, 'User is not logged in')
        try:
            current_user = User.objects.get(email=self.current_user)
        except:
            return self.api_error(500, 'Could not find client user in database')

        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')

        if name or domain:
            # Global profile results
            profiles = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains

            # No results
            if len(profiles) == 0:
                return self.api_response(data={})

            # Connections
            group_users = current_user.all_group_users()
            connections = Connection.objects(profile__in=profiles, user__in=group_users).order_by('-latest_email_out_date')

            # BaseProfileConnections
            ps = []
            for p in profiles:
                bp = BaseProfileConnection(p)
                cs = Connection.objects(profile=p, user__in=group_users).order_by('-latest_email_out_date')
                if len(cs) > 0:
                    bp.connections = cs
                    bp.latest_email_out_date = cs[0]
                    ps.append(bp)

            return self.api_response(data={"profiles": list_to_json_list(ps)})

        else:
            return self.api_error(400, 'Did not include query parameters')

