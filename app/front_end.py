import app.basic, settings
import logging
import tornado.web

########################
### Frontend
########################
class Ember(app.basic.BaseHandler):
  def get(self):
    return self.render('../ember/base.html')
