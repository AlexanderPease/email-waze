import settings
from mongoengine import *
import mongoengine.errors
import logging, random
from db.companydb import Company
from email.utils import parseaddr

mongo_database = settings.get('mongo_database')
connect('profile', host=mongo_database['host'])

class Profile(Document):
    ## Original fields
    # Email is the unique key. Search and create based on email. 
    email = EmailField(required=True, unique=True)
    # Name, ex. Alexander Pease
    name = StringField() 

    ## Derivative fields
    # Domain field derived from canonical email field via function get_domain()
    # Saved in DB for querying
    domain = StringField()
    # Burner is a pass through email that is publicly displayed. 
    # Using term "burner" despite it being a constant in v1
    # meta dict allows you to init self.burner as null, also have multiple nulls
    burner = StringField()
    meta = {
        'indexes': [
            {'fields': ['burner'], 'sparse': True, 'unique': True},
        ]
    }

    def __str__(self):
        return 'Profile: ' + self.name + ' <' + self.email + '>'

    def to_json(self):
        return {
            'id': str(self.id),
            'email': self.email,
            'name': self.name,
            'burner': self.burner,
        }

    def get_domain(self):
        """
        Returns just the domain name of self.email
        Ex: reply.craigslist.com from foo@reply.craigslist.com
        """
        return self.email.split('@')[1]

    def get_domain_title(self):
        """
        Returns domain name minus extension of self.email
        Ex: reply.craigslist from foo@reply.craigslist.com
        """
        return self.domain.split('.')[-2]

    def get_company(self):
        """
        Returns domain name minus extension of self.email
        Ex: reply.craigslist from foo@reply.craigslist.com
        """
        try:
            return Company.objects.get(domain=self.domain)
        except:
            return None

    @classmethod
    def email_exists(cls, email):
        """
        Checks if case-insensitive email exists as a Profile instance

        Returns number of instances if exists, or False
        """
        ps = Profile.objects(email__iexact=email)
        if len(ps) > 0:
            #logging.info('%s profiles contain the case-insensitive email: %s' % (len(ps), email))
            return len(ps)
        else:
            return False

    @classmethod
    def add_new(cls, name, email):
        """
        Creates a new Profile in database (if DNE) and goes through
        all necessary error checking, cleaning, and creation of derivative fields.
        This is effectively __init__ for Profile class. 

        Args:
            Name and email strings

        Returns:
            The Profile instance if successfully created
        """
        try:
            p, created = Profile.objects.get_or_create(email=email) # This automatically saves()
            if p and created:
                # Email is the unique key, case-insensitive
                if Profile.email_exists(email) > 1:
                    p.delete()
                    return

                # Only add attributes here. Don't overwrite attributes if already created
                p.name = name
                p.domain = p.get_domain()
                p.save() 
                # Brief set of rules to ignore certain emails
                if 'reply' in p.email or 'notify' in p.email or 'notification' in p.email or 'info' in p.domain or len(p.email) > 40 or 'ansatz.me' in p.domain:
                    p.delete()
                    logging.info("%s did not pass tests, not added to database" % email)
                else:
                    #p.set_burner_by_algo()
                    p.save()
                    logging.info('Added to database: %s %s' % (p.name, p.email))
                    return p
            # Attempted to add existing email address
            elif p and not created:
                logging.info('%s already exists, no change to database' % p)
        except mongoengine.errors.NotUniqueError:
            logging.info("Profile of email address %s already exists, no new Profile created" % email)
        except:
            logging.warning("Couldn't add Profile: %s <%s>" % (name, email))


# UNUSED
    # Obscured self.email by generating random string. 
    # This is just a string, doesn't include our domain. 
    # Ex: 1493458459, NOT 1493458459@ansatz.me
    #email_obscured = StringField(unique=True) 

    # When this address was last emailed. Helps guess if an email address is still being used or not
    #last_emailed = DateTimeField()
    #clicks = IntField() # How many times this link was clicked

    # Other possible names for this email address
    #other_names = ListField(field=StringField(), default=list)

    # Graph fields, for future use
    #emailed_by = ListField(field=DictField(), default=list) # or look at one to many with listfields
    #emailed_to = ListField(field=DictField(), default=list)

    """
    def __init__(self, *args, **kwargs):
        # Set default burner...
        if 'burner' not in kwargs.keys():
            kwargs['burner'] = 'default'
            burner_flag = True
        else:
            burner_flag = False

        Document.__init__(self, *args, **kwargs)

        # ...so I can modify burner to real value after instantiation
        if self and burner_flag:
            self.set_burner_by_algo(overwrite=True)
    """

    '''
    def set_burner_by_algo(self, overwrite=False):
        """
        Sets burner email string for a Profile based on an algorithm 
        Set overwrite=True or else function does nothing if self.burner already exists
        """
        if not self.burner or (self.burner and overwrite):
            burner = self.name.lower()

            # Remove domain name and title
            if self.get_domain() in burner:
                burner = burner.replace(self.get_domain(), "")
            if self.get_domain_title() in burner:
                burner = burner.replace(self.get_domain_title(), "")

            # Remove unsanitary characters
            for c in "- @'()/.,:;?<>[]{}!#$%^&*":
                burner = burner.replace(c, "")
            
            # If nothing left in burner, set to random string of numbers
            if burner == "":
                burner = '%030x' % random.randrange(16**30)

            # Enforce reasonable length
            burner = burner[:30]

            # Add to Profile. If burner is not unique, add a digit afterwards
            # Ex: alexander is taken, try alexander1, then alexander2, etc. 
            flag = 1
            while flag:
                try:
                    logging.info("Attempting to programatically add burner: %s" % burner)
                    self.burner = burner
                    self.save()
                    logging.info("Added burner: %s" % burner)
                    flag = False # Exit loop
                except Exception as e:
                    # Add number to end of burner if necessary.
                    # Remove previous number if this is not first time
                    # Ex: avoids foo123, instead gives foo3
                    if flag == 1:
                        burner = burner + str(flag)
                    else:
                        burner = burner[:-len(str(flag-1))] + str(flag)
                    flag = flag + 1
    '''

    '''
    @classmethod
    def email_exists(cls, email):
        """
        Checks if case-insensitive email exists as a Profile instance

        Returns number of instances if exists, or False
        """
        ps = Profile.objects(email__icontains=email)
        if len(ps) > 0:
            logging.info('%s profiles contain the case-insensitive email: %s' % (len(ps), email))
            return len(ps)
        else:
            return False
    '''

    '''
    @classmethod
    def add_from_gmail_message_header(cls, msg_header):
        """
        Takes a dict message header from GetMessageHeader() and 
        adds to/creates entries in Profile database if necessary

        Args:
            msg_header: A message header dict returned by GetMessageHeader(). 

        Returns:
            True if a new Profile document was added to database.
        """ 
        """
        header_list = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc'] # Also Date
        for header in header_list:
            if header in msg_header.keys():
                field = parseaddr(msg_header[header]) # Allows local emails addresses unfortunately
                logging.debug(field)
                name = field[0]
                email = field[1].lower() 
                if name and email: # Only add if both are available 
                    Profile.add_new(name=name, email=email)
            else:
                logging.debug('No %s field in header (output in line below)' % header)
                logging.debug(msg_header)
    '''



