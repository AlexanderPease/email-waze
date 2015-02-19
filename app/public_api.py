import app.basic, settings, ui_methods, tornado.web
import logging
from mongoengine.queryset import Q
from db.profiledb import Profile
from db.userdb import User
from db.companydb import Company
from db.connectiondb import Connection
from db.groupdb import Group
from connectionsets import CompanyConnectionSet
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

        ### Search parameters
        # Simple search
        q = self.get_argument('q', '')
        # Advanced search
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')
        company = self.get_argument('company', '')
        # Exact ID search
        company_id = self.get_argument('company_id', '')
        # Select groups
        group_id = self.get_argument('group_id', '')
        # Check for no parameters
        if not q and not name and not domain and not company_id:
            return self.api_error(400, 'Did not include query parameters')

        results = {}
        ### Profiles
        # Default to simple search if present
        if q:
            ''' AND query
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
            '''
            # Case-insensitive regex
            q_regex = re.compile(q, re.IGNORECASE)
            # Construct query
            profiles = Profile.objects(__raw__={
                "$or": [
                    {
                        "name": q_regex
                    },
                    {
                        "domain": q_regex
                    }
                ]
            })
            results['results_msg'] = 'Results for "%s"' % q
        # Exact ID search
        elif company_id:
            company = Company.objects.get(id=company_id)
            profiles = Profile.objects(domain=company.domain)
            results['results_msg'] = company.name
        # Advanced search query. Specific fields are searched
        else:
            # Global profile results
            profiles = Profile.objects(name__icontains=name, email__icontains=domain) # case-insensitive contains
            results['results_msg'] = 'Results for "%s %s"' % (name, domain)

        # No results
        if len(profiles) == 0:
            return self.api_response(data={})

        ### BaseProfileConnections
        if group_id == 'self':
            group_users = [current_user]
        elif group_id and group_id != 'all':
            try:
                group = Group.objects.get(id=group_id, users=current_user)
                group_users = group.users
            except:
                group_users = current_user.all_group_users()
        else:
            group_users = current_user.all_group_users()
        ps = [] # List of BaseProfileConnections
        cs_all = [] # Keep track of all Connections for all Profiles
        for p in profiles:
            cs = Connection.objects(profile=p, user__in=group_users)
            if len(cs) > 0:
                bp = BaseProfileConnection(p, cs, current_user)
                ps.append(bp)
                cs_all += list(cs)
        if len(ps) == 0:
            return self.api_response(data={})
        else:
            results['profiles'] = list_to_json_list(ps)

        # Company-level results stats
        companies = CompanyConnectionSet.package_connections(cs_all, self.user)
        results['companies'] = list_to_json_list(companies)

        return self.api_response(results)

# Returns True if d2 is later than d1
def later_date(d1, d2):
    if not d1:
        return True
    elif not d2:
        return False
    elif d1 > d2:
        return False
    else:
        return True



