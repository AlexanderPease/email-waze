import tornado.web
import requests
import settings
import simplejson as json
import os
import httplib
import logging
#from postmark import PMMail

class BaseHandler(tornado.web.RequestHandler):
  def __init__(self, *args, **kwargs):
    super(BaseHandler, self).__init__(*args, **kwargs)
    #user = self.get_current_user()
    #css_file = "%s/css/threatvector.css" % settings.tornado_config['static_path']
    #css_modified_time = os.path.getmtime(css_file)
      
    self.vars = {
      #'user': user,
      #'css_modified_time': css_modified_time
    }
                
  def render(self, template, **kwargs):
    # add any variables or functions we want available in all templates
    kwargs['user_obj'] = None
    kwargs['settings'] = settings 
    kwargs['current_user_name'] = self.current_user_name
    kwargs['current_user_staff'] = self.current_user_staff
    kwargs['body_location_class'] = ""
    
    if 'msg' not in kwargs.keys():
      kwargs['msg'] = ""
    if 'err' not in kwargs.keys():
      kwargs['err'] = ""

    if self.request.path == "/":
      kwargs['body_location_class'] = "home"
  
    super(BaseHandler, self).render(template, **kwargs)

  
  def get_current_user(self):
    """
    Function that controls self.current_user (Tornado handles this on back end)
    Use the user's email as the identifying property
    """
    return self.get_secure_cookie("user_email")

  def current_user_name(self):
    return self.get_secure_cookie("user_name")


  def current_user_staff(self):
    """
    Returns True if the current user has staff privileges
    """
    if self.current_user in settings.get('staff'):
      return True
    else:
      return False


  ''' Get all arguments and returns in dict form.
      This is difficult because each v is a list, even if only single v for each k'''
  def get_all_arguments(self):
    args = self.request.arguments 
    results = {}
    for arg in args.items():
      results[arg[0]] = arg[1][0] 
    return results

  def send_email(self, from_address, to_address, subject, html_text, cc=None, bcc=None, reply_to=None):
    
    logging.info('entered send_email')
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
    else:
      logging.warning('Email not sent successfully. Status code %s' % request.status_code)
      logging.warning(request)

  ''' Sends email using PostMark'''
  '''
  def send_email(self, to, subject, text_body, sender="postmark@followthevote.org",):
    message = PMMail(api_key = settings.get('postmark_api_key'),
                   sender = sender,
                   to = to,
                   subject = subject,
                   text_body = text_body,
                   tag = None)
    message.send()
  '''
      
  ''' Optional HTML body supercedes plain text body in SendGrid API'''
  '''
  def send_email(self, from_user, to_user, subject, text, html=None, from_name=None):
    if settings.get('environment') != "prod":
      logging.info("If this were prod, we would have sent email to %s" % to_user)
      return
    else:
        return requests.post(
          "https://sendgrid.com/api/mail.send.json",
          data={
            "api_user":settings.get('sendgrid_user'),
            "api_key":settings.get('sendgrid_secret'),
            "from": from_user,
            "to": to_user,
            "subject": subject,
            "text": text,
            "html": html,
            "fromname": from_name
          },
          verify=False
        )
    '''
