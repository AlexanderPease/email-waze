import app.basic, settings, ui_methods
import logging
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection

########################
### StripeBasic
### /stripe/basic
########################
class StripeBasic(app.basic.BaseHandler):
    """
    For basic recurring monthly plan. User who signs up bears cost of all Users
    in the groups that he/she is an admin of
    """
    def post(self):
        token_id = self.get_argument('token_id', '')
        email = self.get_argument('emails', '')
        logging.info('HIT TEST API!!!!!!!!!!!!')
        logging.info(token_id)
        logging.info(email)
        return self.api_response(data=None)


