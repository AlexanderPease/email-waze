import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError
import clearbit
clearbit.key = settings.get('clearbit_key')

mongo_database = settings.get('mongo_database')
connect('company', host=mongo_database['host'])

#CLEARBIT_COMPANY_URL = 'https://company.clearbit.co/v1/companies/domain/'

class Company(Document):
    # I've forced domains to be lowercase
    domain = StringField(required=True, unique=True)
    # Date queried Clearbit
    date_queried_clearbit = DateTimeField()
    # Company info from clearbit
    clearbit = DictField()

    # Derivative fields:
    name = StringField()

    def __init__(self, *args, **kwargs):
        # Force lowercase domain field
        kwargs['domain'] = kwargs['domain'].lower()
        Document.__init__(self, *args, **kwargs)

    def __str__(self):
        if self.clearbit:
            return 'Company: %s (%s)' % (self.clearbit['name'], self.domain)
        elif self.date_queried_clearbit:
            return 'Company: %s. Clearbit returned no info on %s' % (self.domain, self.date_queried_clearbit)
        else:
            return 'Company: %s' % self.domain

    def get_name(self):
        """ 
        Gets the name of this doc. Only option atm is from Clearbit
        """
        if self.clearbit:
            if 'name' in self.clearbit.keys():
                return self.clearbit['name']
        return 'N/A'

    def update_clearbit(self, overwrite=False):
        """
        Updates info by calling Clearbit API. 

        Args:
            overwrite is a flag that will call Clearbit API even if data
            has already been returned before. This is to minimize expensive API
            calls. 

        Note: API doesn't count redundant pings against monthly limit!
        """
        if not self.date_queried_clearbit or overwrite:
            logging.info('Sending request to Clearbit for %s' % self.domain)
            try:
                company = clearbit.Company.find(domain=self.domain, stream=True)
            except URLError, e:
                if e.code == 404:
                    # No data for this company was found. Mark as queried
                    self.date_queried_clearbit = datetime.datetime.now()
                    self.save()
                logging.info('Clearbit error code: %s' % e)
                return 

            if 'error' in info.keys():
                # Look up is queued. Just ignore for now and it will execute
                # next time script is run
                logging.warning(info)
                return

            self.date_queried_clearbit = datetime.datetime.now()
            self.clearbit = info
            logging.info(self.clearbit)
            name = self.clearbit['name']
            if name:
                self.name = name
            logging.info('Added clearbit for company: %s' % self)
            self.save()


