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
        
    	print name
    	print domain
        results = Profile.objects(name__icontains=name, email__icontains=domain).order_by('name') # case-insensitive contains
    else:
        results = None
    return self.render('public/index.html', results=results, email_obscure=ui_methods.email_obscure)





