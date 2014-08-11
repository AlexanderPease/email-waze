import app.basic
from db.politiciandb import Politician
from sunlight import congress 
from geopy import geocoders
import re
import ui_methods 


########################
### Homepage
########################
class Index(app.basic.BaseHandler):
  def get(self):
    name = self.get_argument('name', '')
    results = Profile.objects.get_all(name__icontains=name)

    return self.render('public/index.html')