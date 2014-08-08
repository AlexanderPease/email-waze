import sys, os
try: 
    sys.path.insert(0, '/Users/AlexanderPease/git/email-waze')
    import settings
except:
    pass
from db import profiledb

import httplib2
#import logging
from email.utils import parseaddr

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from googleapiclient import errors


def ListMessagesMatchingQuery(service, user_id, query=''):
  """
  List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id, q=query).execute()

    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def GetMessage(service, user_id, msg_id):
  """
  Get a Message with given ID.

  Args:
  	service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

def GetMessageHeader(msg):
  """
  Gets the email header info from a GMail message dict

  Args:
  	msg: A message dict returned by GetMessage(). 

  Returns:
    A dict containing email header info
  """
  try: 
  	headers = msg['payload']['headers']
  except:
  	print 'Message passed to GetMessageHeader has no headers'
  	return

  header_list = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc']
  info = {}
  
  for header in headers:
  	if header['name'] in header_list:
  		info[header['name']] = header['value']

  return info

'''
def CleanMessageHeader(msg_header):
	  """
	  Cleans the message header dict from GetMessageHeader 
	  so that fields can be saved to database

	  Args:
	  	msg_header: A message header dict returned by GetMessageHeader(). 

	  Returns:
	    The argument, with modifications
	  """
'''


def AuthorizeService():
	"""
	Logs into GMail. From GMail API tutorial. 

	Returns:
		service: Authorized Gmail API service instance.
	"""
	# Path to the client_secret.json file downloaded from the Developer Console
	CLIENT_SECRET_FILE = 'local/client_secret_181358812254-8kl613h65ce75p2jvtuh64hibcfu1nch.apps.googleusercontent.com.json'

	# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
	# All read/write operations except immediate, permanent deletion of threads and messages, bypassing Trash.
	OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.modify'

	# Location of the credentials storage file
	STORAGE = Storage('gmail.storage')

	# Start the OAuth flow to retrieve credentials
	flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
	http = httplib2.Http()

	# Try to retrieve credentials from storage or run the flow to generate them
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid:
	  credentials = run(flow, STORAGE, http=http)

	# Authorize the httplib2.Http object with our credentials
	http = credentials.authorize(http)

	# Build the Gmail service from discovery
	service = build('gmail', 'v1', http=http)
	return service


def main():
	print 'starting'
	gmail_service = AuthorizeService()
	print 'have service'
	messages = ListMessagesMatchingQuery(gmail_service, 'me')
	
	# Iterate through all messages and save email addresses to database
	for msg_info in messages:
		msg = GetMessage(gmail_service, 'me', msg_info['id'])
		header = GetMessageHeader(msg)
		#header = CleanMessageHeader(header)
		if 'From' in header.keys():
			print parseaddr(header['From']) # Allows local emails addresses unfortunately
		else:
			print header






if __name__ == "__main__":
    main()
