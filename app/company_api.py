import settings
import tornado.web
import os
import logging
from tornado.escape import json_encode

########################
### Returns JSON list of all companies in companydb
### /api/company/list
########################
class ListCompanies(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.dirname, self.filename = os.path.split(path)
        logging.info(self.dirname)
        logging.info(self.filename)
        super(ListCompanies, self).initialize(self.dirname)

    def get(self, path=None, include_body=True):
        logging.info('get')
        logging.info(self.filename)
        # Ignore 'path'.
        super(ListCompanies, self).get(self.filename, include_body)




