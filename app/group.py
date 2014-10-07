import app.basic, settings, ui_methods
import logging
import tornado.web
from db.groupdb import Group


########################
### Create a new group
### /group/create
########################
class CreateGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render('group/group_edit.html')

########################
### Edit a group. Use group document id string as identifier. 
### /group/(?P<group>[A-z-+0-9]+)/edit
########################
class EditGroup(app.basic.BaseHandler):
    @tornado.web.authenticated
    def get(self, group=None):
        if not group:
            pass #problem
        pass
        return self.render('group/group_edit.html', group=g)




