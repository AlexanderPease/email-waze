import tornado.web
import requests
import settings
import simplejson as json
import os
import httplib
import logging
from db.userdb import User


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
        kwargs['current_user_casual_name'] = self.current_user_casual_name
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


    # Left over from Nick. Not using yet. kwargs above. 
    def current_user_name(self):
        return self.get_secure_cookie("user_name")

    def current_user_casual_name(self):
        """
        Returns casual name of the logged in user
        Ex: "Alexander"
        """
        try:
            return User.objects.get(email=self.current_user).casual_name()
        except:
            return self.get_secure_cookie("user_name")


    def current_user_staff(self):
        """
        Returns True if the current user has staff privileges
        """
        if self.current_user in settings.get('staff'):
            return True
        else:
            return False


    def get_all_arguments(self):
        """
        Get all arguments and returns in dict form.
        This is difficult because each v is a list, even if only single v for each k
        """
        args = self.request.arguments 
        results = {}
        for arg in args.items():
            results[arg[0]] = arg[1][0] 
        return results


    def send_email(self, from_address, to_address, subject, html_text, cc=None, bcc=None, reply_to=None):
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

    def api_response(self, data):
        """
        Return an api response in the proper output format with status_code == 200
        """
        self.write_api_response(data, 200, "OK")


    def api_error(self, status_code, status_txt, data=None):
        """
        Return an api error in the proper output format
        """
        self.write_api_response(status_code=status_code, status_txt=status_txt, data=data)


    def write_api_response(self, data, status_code, status_txt):
        """
        Return an api error based on the appropriate request format (ie: json)
        """
        format = self.get_argument('format', 'json')
        callback = self.get_argument('callback', None)
        if format not in ["json"]:
            status_code = 500
            status_txt = "INVALID_ARG_FORMAT"
            data = None
            format = "json"
        response = {'status_code':status_code, 'status_txt':status_txt, 'data':data}

        if format == "json":
            data = json.dumps(response)
            if callback:
                    self.set_header("Content-Type", "application/javascript; charset=utf-8")
                    self.write('%s(%s)' % (callback, data))
            else:
                    self.set_header("Content-Type", "application/json; charset=utf-8")
                    self.write(data)
            self.finish()


    def write_error(self, status_code, **kwargs):
        self.require_setting("static_path")
        if status_code in [404, 500, 503, 403, 405]:
            filename = os.path.join(self.settings['static_path'], '%d.html' % status_code)
            if os.path.exists(filename):
                f = open(filename, 'r')
                data = f.read()
                f.close()
                return self.write(data)
        return self.write("<html><title>%(code)d: %(message)s</title>" \
                "<body class='bodyErrorPage'>%(code)d: %(message)s</body></html>" % {
                "code": status_code,
                "message": httplib.responses[status_code],
        })


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
