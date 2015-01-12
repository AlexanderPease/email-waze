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
        json_list = []
        for c in Company.objects:
          if c.clearbit:
            logging.info(c.clearbit)
            json_list.append(json_encode(c.clearbit['name']))
        logging.info(json_list)
        return self.write(json_list)




