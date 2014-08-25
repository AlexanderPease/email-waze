import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    print 'sending email'
    self.send_email('alexander@usv.com', 'me@alexanderpease.com', 'test', 'test_body')
    print 'sent'



    name = self.get_argument('search', '')
    if name:
        results = Profile.objects(name__icontains=name).order_by('name') # case-insensitive contains
        # Extend search possibilities
    else:
        results = None
    return self.render('public/index.html', results=results, email_obscure=ui_methods.email_obscure)





