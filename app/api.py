import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile


########################
### ProfileSearch
### /api/profilesearch
########################
class ProfileSearch(app.basic.BaseHandler):
    def get(self):
        name = self.get_argument('name', '')
        domain = self.get_argument('domain', '')

        if name or domain:
            results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
            if results:
                return self.api_response(data=results.to_json())

        return self.api_response(data=None)


########################
### ProfileSearch
### /api/groupinboxsearchfordomain
########################
class GroupInboxSearchForDomain(app.basic.BaseHandler):
    def get(self, user, group, domain):
        """
            For a logged in user, searches the inboxes of all of the other users
            for which he/she is in a group with for emails with a given domain
        """
        return self.api_response(data=None)




