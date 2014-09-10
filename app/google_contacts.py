from db.userdb import User

import atom.data
import gdata.data
import gdata.contacts.client
import gdata.contacts.service
import gdata.gauth
import logging

def ContactsJob(user):
  gd_client= user.get_gd_client()

  # GetContacts defaults to retunr 25 contacts, so extend query first
  query = gdata.contacts.client.ContactsQuery()
  query.max_results = 99999 # crazy high number to get all contacts
  feed = gd_client.GetContacts(q=query)

  for i, entry in enumerate(feed.entry):
    try:
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
    except:
      print 'FAIL'






        