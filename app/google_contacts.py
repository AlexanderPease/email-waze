from db.userdb import User
from db.profiledb import Profile

import gdata.contacts.client
import logging
import mongoengine.errors

def ContactsJob(user):
    """
    Creates a Profile document for every contact from Google Contacts API
    for User user

    Args: 
        user: A User object 
    """
    gd_client= user.get_gd_client()

    if gd_client:
        query = gdata.contacts.client.ContactsQuery()  
        query.max_results = 99999 # GetContacts defaults to retunr 25 contacts, so extend query first

        try: 
            feed = gd_client.GetContacts(q=query)
        except:
            logging.warning('User %s does not have Google Contacts API permission' % user)
            return
        
        # Add all email addresses from feed on best effort basis
        for i, entry in enumerate(feed.entry):
            try:
                if entry.name.full_name.text:
                    for email in entry.email:
                        if email.primary and email.primary == 'true' and email.address:
                            logging.info('Adding: %s %s' % (entry.name.full_name.text, email.address))
                            Profile.add_new(name=entry.name.full_name.text, email=email.address)
            except:
                logging.info('Error adding entry') # Most likely due to lack of name in the entry
        return True

    else:
        logging.warning('User %s most likely does not have Contacts oauth scope', user)



    ''' From tutorial, helps identify useful entries
    if entry.name.full_name.text:
                print '\n%s %s' % (i+1, entry.name.full_name.text)
            if entry.content:
                print '    %s' % (entry.content.text)
            # Display the primary email address for the contact.
            for email in entry.email:
                if email.primary and email.primary == 'true':
                    print '    %s' % (email.address)
            # Show the contact groups that this contact is a member of.
            for group in entry.group_membership_info:
                print '    Member of group: %s' % (group.href)
            # Display extended properties.
            for extended_property in entry.extended_property:
                if extended_property.value:
                    value = extended_property.value
                else:
                    value = extended_property.GetXmlBlob()
                print '    Extended Property - %s: %s' % (extended_property.name, value)
    '''



                