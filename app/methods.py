def blacklist_email(email):
    '''
    Returns True if email is blacklisted, False if not
    '''
    for r in __reject_email_domain():
        if r in email_domain(email):
            return True
    for r in __reject_email_local():
        if r in email:
            return True
    return False


def email_domain(email):
    return email.split('@')[1]

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