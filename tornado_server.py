import os
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
import logging

# settings is required/used to set our environment
import settings 
import templates

import app.basic, app.public, app.admin, app.email
import app.googleauth

#import newrelic.agent I also deleted newrelic.ini. Need to re-add if we want 
#path = os.path.join(settings.get("project_root"), 'newrelic.ini')
#newrelic.agent.initialize(path, settings.get("environment"))

class Application(tornado.web.Application):
  def __init__(self):

    debug = (settings.get('environment') == "dev")

    app_settings = {
      "cookie_secret" : "change_me",
      "login_url": "/auth/twitter",
      "debug": debug,
      "static_path" : os.path.join(os.path.dirname(__file__), "static"),
      "template_path" : os.path.join(os.path.dirname(__file__), "templates"),
    }

    handlers = [
      # Email handling
      (r"/email/forward", app.email.Forward),

      # Google auth
      (r"/auth/google/?", app.googleauth.Auth),
      (r"/auth/google/return/?", app.googleauth.AuthReturn),
      (r"/auth/logout/?", app.googleauth.LogOut),

      # Admin
      (r"/admin", app.admin.AdminHome),
      (r"/admin/db_profiles", app.admin.DB_Profiles),

      # Public
      (r'/$', app.public.Index),
    ]

    tornado.web.Application.__init__(self, handlers, **app_settings)

def main():
  tornado.options.define("port", default=8001, help="Listen on port", type=int)
  tornado.options.parse_command_line()
  logging.info("starting tornado_server on 0.0.0.0:%d" % tornado.options.options.port)
  http_server = tornado.httpserver.HTTPServer(request_callback=Application(), xheaders=True)
  http_server.listen(tornado.options.options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
