import app.basic, settings, ui_methods
import logging
from db.userdb import User
from db.groupdb import Group
import stripe

FREE_QUANTITY_TIER = 0

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
        email = self.get_argument('email', '')
        logging.info(token_id)
        logging.info(email)

        # Find user associated with email
        try:
            u = User.objects.get(email=email)
        except:
            return self.api_error(400, 'Could not find user from email arg')

        # Find quantity to charge User for
        groups = u.get_groups()
        quantity = 0
        for g in groups:
            if len(g.users) > FREE_QUANTITY_TIER:
                quantity = quantity + len(g.users)

        stripe.api_key = "sk_test_eSsyIJ6aEDaUjq8l8QJT7EKi"

        # Existing Stripe Customer
        if u.stripe_id:
            # Update credit card token and plan size
            customer = stripe.Customer.retrieve(u.stripe_id)
            customer.card = token_id
            customer.save()
            subscription = customer.subscriptions.retrieve(u.stripe_subscription_id)
            subscription.quantity = quantity
            subscription.save()
        # New Stripe Customer
        else: 
            # Create customer
            customer = stripe.Customer.create(
                card=token_id,
                email=email
            )
            u.stripe_id = customer.id
            u.save()

            # Add subscription to customer
            subscription = customer.subscriptions.create(
                plan='monthly_per_user_basic',
                quantity=quantity
            )
            u.stripe_subscription_id = subscription.id
            u.save()

        return self.api_response(data=None)


