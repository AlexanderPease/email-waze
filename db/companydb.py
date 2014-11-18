import settings
from mongoengine import *
import logging
import base64
from urllib2 import Request, urlopen, URLError

mongo_database = settings.get('mongo_database')
connect('company', host=mongo_database['host'])

CLEARBIT_COMPANY_URL = 'https://company.clearbit.co/v1/companies/domain/'

class Company(Document):
    domain = StringField(required=True, unique=True)
    # Date queried Clearbit
    date_queried_clearbit = DateTimeField()
    # Company info from clearbit
    clearbit = DictField()

    def __str__(self):
        if self.clearbit:
            return 'Company: %s (%s)' % (self.clearbit.name, self.domain)
        elif self.date_queried_clearbit:
            return 'Company: %s. Clearbit returned no info on %s' % (self.id, self.date_queried_clearbit)
        else:
            return 'Company: %s' % self.domain

    def update_clearbit(self, overwrite=False):
        """
        Updates info by calling Clearbit API. 

        Args:
            overwrite is a flag that will call Clearbit API even if data
            has already been returned before. This is to minimize expensive API
            calls
        """
        if not self.date_queried_clearbit or overwrite:
            logging.info('call')
            request = Request(CLEARBIT_COMPANY_URL + self.domain)
            base64string = base64.encodestring('%s:' % settings.get('clearbit_key')).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            logging.info(request)
            try:
                response = urlopen(request)
                info = response.read()
                logging.info(info)
            except URLError, e:
                logging.info('Clearbit error code: %s' % e)