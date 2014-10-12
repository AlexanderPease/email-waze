from db.profiledb import Profile
from db.userdb import User

import httplib2, datetime, logging
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run
from googleapiclient import errors
from email.utils import parsedate

import datetime, time, timeout_decorator


def ListMessagesMatchingQuery(service, user_id, query=''):
    """
    List all Messages of the user's mailbox matching the query.
    Observed (but not documented) as in reverse chronological order

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
            response = service.users().messages().list(userId=user_id, 
                                                    q=query,
                                                    pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        logging.warning('An error occurred: %s' % error)
    except KeyError:
        logging.warning('KeyError')


#@timeout_decorator.timeout(30) # Give Google 30 seconds to respond
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
        logging.debug('getting message from service.users().messages().get()')
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        logging.debug('service.users().messages().get() returns %s' % message)
        return message
    except errors.HttpError, error:
        logging.warning('An error occurred: %s' % error)

def GetMessageHeader(msg):
    """
    Gets the email header info from a Gmail message dict

    Args:
        msg: A message dict returned by GetMessage(). 

    Returns:
        A dict containing email header info
    """
    try: 
        headers = msg['payload']['headers']
    except:
        logging.warning('Message passed to GetMessageHeader has no headers')
        return None

    header_list = ['Delivered-To', 'Return-Path', 'From', 'To', 'Cc', 'Date']
    msg_header = {}

    for header in headers:
        if header['name'] in header_list:
            msg_header[header['name']] = header['value']

    return msg_header

def ParseDate(date_string):
    """
    Takes date string specified by RFC 2822 and returns datetime instance
    """
    return datetime.datetime.fromtimestamp(time.mktime(parsedate(date_string)))


#FAIL_THRESHOLD = 10
#def GmailJob(user):
    """
    Updates database with a signed up user's contacts by going through every
    single email in the inbox and adding new addresses to the database.
    This is the original scraping method used. 

    Args: user is a User profile object
    """
    """
    if not isinstance(user, User):
        logging.warning("User type argument incorrect")
        return

    gmail_service = user.get_service('gmail')
    if gmail_service:
        # Determine start date of messages to search through. If job has
        # not been run before, query is blank (for all messages)
        start_date = user.gmail_job_start_date()
        if start_date:
            q = 'after:' + start_date.strftime('%Y/%m/%d')
        else:
            q = ''

        logging.info("Authorized Gmail service, retrieving all unseen messages...")
        messages = ListMessagesMatchingQuery(service=gmail_service, user_id='me', query=q)

        # Iterate through all messages and save email addresses to database
        # This is a best effort script
        total_num = len(messages)
        counter = 0
        fail_counter = 0
        added = 0
        for msg_info in messages:
            logging.info("Checking message of id: %s (%s of %s total)" % (msg_info['id'], counter, total_num))
            try:
                msg = GetMessage(gmail_service, 'me', msg_info['id'])
                header = GetMessageHeader(msg)
                if header:
                    result = Profile.add_from_gmail_message_header(header) # adds to database
                    if result:
                        added = added + 1
            except:
                logging.warning("Exception raised in GmailJob, incrementing fail_counter to %s" % fail_counter)
                fail_counter = fail_counter + 1

            counter = counter + 1
            logging.info('%s Profiles added by %s' % (added, user))
            
            # If FAIL_THRESHOLD number of messages have failed, save and exit the partial job
            if fail_counter >= FAIL_THRESHOLD:
                # Get latest message date of added messages
                for msg_info in messages[counter:0:-1]: # Iterate backwards
                    if 'Date' in header.keys():
                        date = header['Date']
                        break 

                user.gmail_job.last_job = datetime.datetime.now()
                user.gmail_job.fail_date = date
                user.gmail_job.success = False
                user.save()
                return

        # Save completed job specs to user.gmail_job
        user.gmail_job.last_job = datetime.datetime.now()
        user.gmail_job.fail_date = None
        user.gmail_job.success = True
        user.save()
        return
    """


