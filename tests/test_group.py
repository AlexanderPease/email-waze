import settings, logging
from db.groupdb import Group
from db.userdb import User

def test_group_class():
    """
    Series of tests for the Group class
    """
    # Prep
    for g in Group.objects:
        g.delete()

    u = User.objects.get(email='alexander@usv.com')
    u2 = User.objects.get(email='me@alexanderpease.com')
    u3 = User.objects.get(email="brittany@usv.com")
    u4 = User.objects.get(email="gillian@usv.com")

    # Create a group
    g = Group(name='test', users=[u])
    g.save()
    assert g.users == [u]

    # Add a user to existing group
    g.add_user(u2)
    assert g.users.sort() == [u, u2].sort()

    # Remove a user from an existing group
    g.remove_user(u2)
    assert g.users == [u]

    # Remove a user that is not in group
    g.remove_user(u2)
    assert g.users == [u]

    # Add a user that is already in group
    g.add_user(u)
    assert g.users == [u]

    # Test querying
    assert Group.objects.get(users=u) == g
    g2 = Group(name="test2", users=[u, u3])
    g2.save()
    g3 = Group(name="test3", users=[u3])
    g3.save()
    assert list(Group.objects(users=u)).sort() == [g, g2].sort()

    # Query users in groups that u is in
    g4 = Group(name="test4", users=[u, u3])
    assert u.all_group_users().sort() == [u, u3].sort()

    # Test group settings
    g4.set_domain_setting('usv.com')
    g4.save()
    g4.add_user(u4) # Should add
    g4.add_user(u2) # Should not add
    assert g4.users.sort() == [u, u3, u4].sort()

    for g in Group.objects:
        g.delete()
