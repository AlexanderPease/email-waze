import settings
from mongoengine import *
import logging, base64, datetime, json
from urllib2 import Request, urlopen, URLError

mongo_database = settings.get('mongo_database')
connect('company', host=mongo_database['host'])

CLEARBIT_COMPANY_URL = 'https://company.clearbit.co/v1/companies/domain/'

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
        logging.info('init')
        # Force lowercase domain field
        kwargs['domain'] = kwargs['domain'].lower()
        Document.__init__(self, *args, **kwargs)

    def __str__(self):
        if self.clearbit:
            return 'Company: %s (%s)' % (self.clearbit['name'], self.domain)
        elif self.date_queried_clearbit:
            return 'Company: %s. Clearbit returned no info on %s' % (self.id, self.date_queried_clearbit)
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
        """
        if not self.date_queried_clearbit or overwrite:
            request = Request(CLEARBIT_COMPANY_URL + self.domain)
            base64string = base64.encodestring('%s:' % settings.get('clearbit_key')).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            try:
                response = urlopen(request)
                info = response.read()
                info = json.loads(info)
            except URLError, e:
                logging.info('Clearbit error code: %s' % e)
                return 

            if 'error' in info.keys():
                logging.warning('Error in info dict:')
                logging.warning(info)
            else:
                # Prevents multiple pings to Clearbit for companies he has no info on
                # API doesn't count multiple pings against monthly limit!
                self.date_queried_clearbit = datetime.datetime.now()
                self.clearbit = info
                name = self.clearbit['name']
                if name:
                    self.name = clearbit['name']
                logging.info('Added clearbit for company: %s' % self)
                self.save()


