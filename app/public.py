import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    name = self.get_argument('name', '')
    domain = self.get_argument('domain', '')

    if name or domain:
        results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
        if not results:
        	results = 'empty' # this is passed into to alert user that no results were returned
    else:
        results = None
    #return self.render('public/index.html', results=results, email_obscure=ui_methods.email_obscure)
    return self.render('public/index.html', results=results, email_obscure=Profile.get_domain)





