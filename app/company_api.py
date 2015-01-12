import app.basic, settings, ui_methods, tornado.web
import logging
from tornado.escape import json_encode
from db.companydb import Company

########################
### Returns JSON list of all companies in companydb
### /api/company/list
########################
class ListCompanies(app.basic.BaseHandler):
    def get(self):
      return self.write(self.static_url('company_list.json'))




