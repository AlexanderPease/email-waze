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
        logging.info('called listcompanies')
        logging.info(json_encode(["Facebook","Google","Union Square Ventures"]))
        return self.write(json_encode(["Facebook","Google","Union Square Ventures"]))




