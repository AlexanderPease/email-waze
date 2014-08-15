import tornado.web
import requests
import settings
import simplejson as json
import os
import httplib
import logging
from postmark import PMMail

from db import userdb

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
    kwargs['email_obscure'] = self.email_obscure 
    kwargs['settings'] = settings 
    kwargs['body_location_class'] = ""
    
    if 'msg' not in kwargs.keys():
      kwargs['msg'] = ""
    if 'err' not in kwargs.keys():
      kwargs['err'] = ""

    if self.request.path == "/":
      kwargs['body_location_class'] = "home"
  
    super(BaseHandler, self).render(template, **kwargs)
    
  def get_current_user(self):
    return self.get_secure_cookie("username")

  ''' Get all arguments and returns in dict form.
      This is difficult because each v is a list, even if only single v for each k'''
  def get_all_arguments(self):
    args = self.request.arguments 
    results = {}
    for arg in args.items():
      results[arg[0]] = arg[1][0] 
    return results

  ''' Sends email using PostMark'''
  def send_email(self, to, subject, text_body, sender="postmark@followthevote.org",):
    message = PMMail(api_key = settings.get('postmark_api_key'),
                   sender = sender,
                   to = to,
                   subject = subject,
                   text_body = text_body,
                   tag = None)
    message.send()

  def email_obscure(self, email):
    """
    Obscures an email address

    Args: 
      email: A string, ex: testcase@alexanderpease.com

    Returns
      A string , ex: t*******@alexanderpease.com
      """
    first_letter = email[0]
    string_split = email.split('@')
    obscured = ""
    while len(obscured) < len(string_split[0])-1:
      obscured = obscured + "*"

    return first_letter + obscured + "@" + string_split[1]
      
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
