import tornado.web
import requests
import settings
import simplejson as json
import os
import httplib
import logging
import datetime
import methods
from db.userdb import User


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        try:
            self.user = User.objects.get(email=self.current_user)
        except:
            self.user = None


    def render(self, template, **kwargs):
        # Set current users action in database
        if self.user:
            self.user.last_web_action = datetime.datetime.now()
            self.user.save()

        # add any variables or functions we want available in all templates
        kwargs['user'] = self.user
        kwargs['user_obj'] = None
        kwargs['settings'] = settings 
        kwargs['current_user_staff'] = self.current_user_staff
        kwargs['body_location_class'] = ""
        
        if 'msg' not in kwargs.keys():
            kwargs['msg'] = ""
        if 'err' not in kwargs.keys():
            kwargs['err'] = ""
        if 'show_nav' not in kwargs.keys():
            kwargs['show_nav'] = True
        if 'nav_select' not in kwargs.keys():
            kwargs['nav_select'] = ""
        if 'nav_title' not in kwargs.keys():
            kwargs['nav_title'] = ""

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

    def reject_email_local(self):
        '''
        Returns of list of local email address parts to ignore
        '''
        return ['reply', 'notify', 'notification']

    def reject_email_domain(self):
        '''
        Returns of list of email address domains to ignore
        '''
        return ['craigslist']
