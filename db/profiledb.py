import settings
from mongoengine import *
import mongoengine.errors
import logging, random
from email.utils import parseaddr

mongo_database = settings.get('mongo_database')
connect('profile', host=mongo_database['host'])

class Profile(Document):
    name = StringField() 
    email = EmailField(required=True, unique=True) # This will have to become a list at some point, or have a secondary email list
    
    # Obscured self.email by generating random string. This is just a string, doesn't include our domain. 
    # Ex: 1493458459, NOT 1493458459@ansatz.me
    email_obscured = StringField(unique=True) 


    # When this address was last emailed. Helps guess if an email address is still being used or not
    #last_emailed = DateTimeField()
    clicks = IntField() # How many times this link was clicked

    # Other possible names for this email address
    #other_names = ListField(field=StringField(), default=list)

    # Graph fields, for future use
    #emailed_by = ListField(field=DictField(), default=list) # or look at one to many with listfields
    #emailed_to = ListField(field=DictField(), default=list)

    def __str__(self):
        return self.name + ' <' + self.email + '>'


    ''' Not yet being used
    def increment_clicks(self):
        """
        Increment whenever someone clicks on this Profile's link
        """
        self.clicks = self.clicks + 1
        self.save()
    '''

    def get_domain(self):
        """
        Returns just the domain name of the email address
        Ex: reply.craigslist.com from foo@reply.craigslist.com
        """
        return self.email.split('@')[1]


    @classmethod
    def add_new(cls, name, email):
        """
        Creates a new Profile in database (if DNE) and goes through
        all necessary error checking, cleaning, and creation of derivative fields
        """
        try:
            p, created = Profile.objects.get_or_create(
                            name = name, 
                            email = email, 
                            email_obscured = '%030x' % random.randrange(16**30))
            if p and created:
                # Brief set of rules to ignore certain emails
                if 'reply' in p.email or 'info' in p.get_domain() or len(p.email) > 40 or 'ansatz.me' in p.get_domain():
                    p.delete()
                    logging.info("%s did not pass tests, not added to database" % email)
                else:
                    logging.info('Added to database: %s %s' % (p.name, p.email))

            # Attempted to add existing email address
            elif p and not created:
                logging.info('%s already exists, no change to database' % p)
            else:
                logging.warning("p DNE?!")
                raise Exception
        
            ''' In future save other names?
            if p.name and name not in p.other_names:
                p.other_names = p.other_names.extend(name)
            elif not p.name:
                p.name = name
            else:
                logging.warning("No name added")
                p.delete()
                raise Exception
            '''
        except mongoengine.errors.NotUniqueError:
            logging.info("Profile of email address %s already exists, no new Profile created" % email)
        except:
            logging.warning("Couldn't add Profile: %s <%s>" % (name, email))


    @classmethod
    def add_from_gmail_message_header(cls, msg_header):
        """
        Takes a message header from GetMessageHeader() and 
        adds to/creates entries in Profile database if necessary

        Args:
            msg_header: A message header dict returned by GetMessageHeader(). 
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


    @classmethod
    def add_from_google_contact(cls, contact):
        """
        Takes a message header from GetMessageHeader() and 
        adds to/creates entries in Profile database if necessary

        Args:
            msg_header: A message header dict returned by GetMessageHeader(). 
        """ 
        header_list = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc'] # Also Date
        for header in header_list:
            if header in msg_header.keys():
                field = parseaddr(msg_header[header]) # Allows local emails addresses unfortunately
                logging.debug(field)
                name = field[0]
                email = field[1].lower() 
                if name and email: # Only add if both are available 

                    # Add the email to database
                    try:
                        p, created = Profile.objects.get_or_create(name=name, email=email)
                        
                        # A new email address was added
                        if p and created:
                            p.email_obscured = '%030x' % random.randrange(16**30)
                            p.save()
                            # Brief set of rules to ignore certain emails
                            if 'reply' in p.email or 'info' in p.get_domain() or len(p.email) > 40 or 'ansatz.me' in p.get_domain():
                                p.delete()
                                logging.info("%s did not pass tests, not added to database" % email)
                            else:
                                logging.info('Added to database: %s %s' % (p.name, p.email))

                        # Attempted to add existing email address
                        elif p and not created:
                            logging.info('%s already exists, no change to database' % p)
                        else:
                            logging.warning("p DNE?!")
                            raise Exception

                        
                        ''' # Primary name, or save in other names?
                        if p.name and name not in p.other_names:
                            p.other_names = p.other_names.extend(name)
                        elif not p.name:
                            p.name = name
                        else:
                            logging.warning("No name added")
                            p.delete()
                            raise Exception
                        '''
                    except:
                        logging.warning("Couldn't add email address: %s <%s>" % (name, email))


            else:
                logging.debug('No %s field in header (output in line below)' % header)
                logging.debug(msg_header)

        


        


