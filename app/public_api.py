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
            company = Company.objects.get(id=company_id)
            profiles = Profile.objects(email__icontains=company.domain)
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
            cs = Connection.objects(profile=p, user__in=group_users)
            if len(cs) > 0:
                bp = BaseProfileConnection(p, cs, current_user)
                ps.append(bp)
        results['profiles'] = list_to_json_list(ps)

        # Company stats if a single company was selected
        if company_id: 
            c_stats = {
                'name': company.name,
                'domain': company.domain,
                'num_connections': len(ps)
            }
            if company.clearbit:
                if 'logo' in company.clearbit.keys():
                    c_stats['logo'] = company.clearbit['logo']
            latest_connection = ps[0]
            most_connection = ps[0]
            for bp in ps[1:]:
                if later_date(latest_connection.latest_email_out_date, bp.latest_email_out_date):
                    latest_connection = bp
                if bp.total_emails() > most_connection.total_emails():
                    most_connection = bp
            c_stats['latest_connection'] = latest_connection.to_json()
            c_stats['most_connection'] = most_connection.to_json()
            results['company_stats'] = c_stats

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



