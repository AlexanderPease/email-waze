import app.basic, settings
import logging
from db.profiledb import Profile


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    name = self.get_argument('search', '')
    if name:
        results = Profile.objects(name__icontains=name) # case-insensitive contains
        # Extend search possibilities
    else:
        results = None
    return self.render('public/index.html', results=results)





