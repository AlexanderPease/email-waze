import settings, logging, datetime
from db.profiledb import Profile
from db.userdb import User
from db.connectiondb import Connection
import tasks

def test_onboard_user():
    """
    ONLY RUN THIS TEST ON A DEVELOPMENT DATABASE

    This tests the combination of tasks.onboard_user() and then the upkeep of
    tasks.update_user() that follows each night to get recent emails/contacts

    This test assumes a User of email me@alexanderpease.com and should not have
    any preexisting Connection or Profile documents so as to fully test the 
    performance of the tasks
    """

    # Prep
    Connection.drop_collection()
    logging.info('Deleted all Connection documents')

    Profile.drop_collection()
    logging.info('Deleted all Profile documents')

    u = User.objects.get(email="me@alexanderpease.com")

    # Test onboard_user()
    tasks.onboard_user.delay(u)

    connections = Connection.objects
    profiles = Profile.objecst
    assert len(connections) > 210
    assert len(profiles) == len(connections)


def test_update_user():
    """
    ONLY RUN THIS TEST ON A DEVELOPMENT DATABASE

    This tests the combination of tasks.onboard_user() and then the upkeep of
    tasks.update_user() that follows each night to get recent emails/contacts

    This test assumes a User of email me@alexanderpease.com and should not have
    any preexisting Connection or Profile documents so as to fully test the 
    performance of the tasks
    """ 
    # Reset profile and connections database
    Connection.drop_collection()
    logging.info('Deleted all Connection documents')

    Profile.drop_collection()
    logging.info('Deleted all Profile documents')

    u = User.objects.get(email="me@alexanderpease.com")

    # Run update_user() piecemeal to get all Connections and Profiles again
    u.last_updated = datetime.datetime(2000, 01, 01) # Arbitrary start date
    tasks.update_user(u)

    # Check same number of profiles and connections
    profiles = Profile.objects
    connections = Connection.objects
    logging.info(len(profiles))
    logging.info(len(connections))
    assert len(profiles) == len(profiles)
    assert len(connections) == len(connections)


    logging.info("Finished test_both_jobs()")



