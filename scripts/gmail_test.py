import httplib2

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

"""Get a list of Messages from the user's mailbox.
"""

from googleapiclient import errors


def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

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
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
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

def tutorial_script():
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
	gmail_service = build('gmail', 'v1', http=http)

	# Retrieve a page of threads
	threads = gmail_service.users().threads().list(userId='me').execute()

	# Print ID for each thread
	if threads['threads']:
	  for thread in threads['threads']:
	    pass #print 'Thread ID: %s' % (thread['id'])

	return gmail_service

def main():
	gmail_service = tutorial_script()
	messages = ListMessagesMatchingQuery(gmail_service, "me")
	print messages

if __name__ == "__main__":
    main()
