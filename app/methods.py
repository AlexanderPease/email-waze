import settings
import requests 
import logging

def blacklist_email(email):
    '''
    Returns True if email is blacklisted, False if not
    '''
    domain = email_domain(email)
    if domain:
        for r in __reject_email_domain():
            if r in domain:
                return True
    for r in __reject_email_local():
        if r in email:
            return True
    return False


def email_domain(email):
    '''
    Returns domain of an email address, or None
    '''
    email_split = email.split('@')
    if len(email_split) == 2:
        return email_split[1]
    else:
        return None

def __reject_email_local():
    '''
    Returns of list of local email address parts to ignore
    '''
    return ['reply', 'notify', 'notification']

def __reject_email_domain():
    '''
    Returns of list of email address domains to ignore
    '''
    return ['craigslist', 'amazonses.com', 'googlegroups.com']

def create_object_id_list(objects):
    '''
    Returns of list of ObjectIDs. Preserves order of original list.
    Helpful for stopping database cursor from timing out over long jobs.

    Args:
        objects is a list of MongoEngine Objects
    
    '''
    id_list = []
    if not objects:
        return
    for o in objects:
        id_list.append(o.id)
    return id_list

def send_email(from_address, to_address, subject, html_text, cc=None, bcc=None, reply_to=None):
    '''
    Sends email via MailGun API
    Returns request object if successful, or None
    '''
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(settings.get('domain_name'))
    request = requests.post(request_url, auth=('api', settings.get('mailgun_api_key')), data={
            'from': from_address,
            'to': to_address,
            'cc': cc,
            'bcc': bcc,
            'h:Reply-To': reply_to, 
            'subject': subject,
            'html': html_text
    })
    if request.status_code is 200:
        logging.info('Email to %s sent successfully' % to_address)
        return request
    else:
        logging.warning('Email not sent successfully. Status code %s' % request.status_code)
        logging.warning(request)
        return None
