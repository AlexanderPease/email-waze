import app.basic, settings, ui_methods, tornado.web
import logging
from mongoengine.queryset import Q
from db.profiledb import Profile
from db.userdb import User
from db.companydb import Company
from db.connectiondb import Connection
from connectionsets import GroupConnectionSet
from connectionsets import ProfileConnectionSet
from connectionsets import BaseProfileConnection
from connectionsets import list_to_json_list
import math, re

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

        # Simple search
        q = self.get_argument('q', '')

        # Advanced search
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')
        company = self.get_argument('company', '')

        # Exact ID search
        company_id = self.get_argument('company_id', '')

        # Check for no parameters
        if not q and not name and not domain and not company_id:
            return self.api_error(400, 'Did not include query parameters')

        results = {}
        ### Profiles
        # Default to simple search if present
        if q:
            q_array = q.split(" ") # whitespace delimited
            logging.info(q_array)
            q_regex_array = []
            # Case-insensitive regexs
            for f in q_array:
                q_regex_array.append(re.compile(f, re.IGNORECASE))
            q_array = q_regex_array
            # Construct query
            profiles = Profile.objects(__raw__={
                "$or": [
                    {
                        "name": {"$in": q_array}
                    },
                    {
                        "domain": {"$in": q_array}
                    }
                ]
            })
        # Exact ID search
        elif company_id:
            c = Company.objects.get(id=company_id)
            profiles = Profile.objects(email__icontains=c.domain)
            # Add Company-level stats for this type of search
            c_stats = {
                'name': c.name,
                'domain': c.domain,
                'strongest_connection': 'foo'
            }
            if c.clearbit:
                if 'logo' in c.clearbit.keys():
                    c_stats['logo'] = c.clearbit['logo']

            results['company_stats'] = c_stats
        # Advanced search query. Specific fields are searched
        else:
            # Global profile results
            profiles = Profile.objects(name__icontains=name, email__icontains=domain) # case-insensitive contains

            # No results
            if len(profiles) == 0:
                return self.api_response(data={})

        ### BaseProfileConnections
        group_users = current_user.all_group_users()
        ps = []
        for p in profiles:
            bp = BaseProfileConnection(p)
            cs = Connection.objects(profile=p, user__in=group_users)
            if len(cs) > 0:
                bp.connections = cs
                bp.latest_email_out_date = cs[0]
                ps.append(bp)

        results['profiles'] = list_to_json_list(ps)
        return self.api_response(results)


