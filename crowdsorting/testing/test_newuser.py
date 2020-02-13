from crowdsorting.app_resources.Strings_List import *
from crowdsorting.testing.test_pytest import client
from crowdsorting.testing.utils.testing_utils import login, logout, mock_user, mock_cas
from pytest_mock import mocker
import crowdsorting

def test_vanilla_new_user(client):
    res = client.get('/')
    assert b'To use this app, please log in at the upper right corner.' in res.data
    with client.session_transaction() as sess:
        sess['matthew'] = True
    res = client.get('/newuser')
    assert b'Please enter your name below' in res.data

    data = {
            'firstName': 'Han',
            'lastName': 'Solo'

    }

    with client.session_transaction() as sess:
        sess['user'] = mock_user('hsolo@gmail.com', False)
    res = client.post('/newuser', data=data, follow_redirects=True)
    assert b'My Projects' in res.data
    assert b'hsolo@gmail.com' in res.data

def test_vanilla_cas_user(client):
    res = client.get('/')
    assert b'To use this app, please log in at the upper right corner.' in res.data
    res = client.get('/newuser')
    assert b'Please enter your name below' in res.data

    data = {
            'firstName': 'Han',
            'lastName': 'Solo'

    }

    with client.session_transaction() as sess:
        sess['user'] = mock_user('hsolo@gmail.com', False)
    crowdsorting.routes.cas = mock_cas('hsolo')
    res = client.post('/newcasuser', data=data, follow_redirects=True)
    assert b'My Projects' in res.data
    assert b'hsolo@byu.edu' in res.data

def test_bad_user(client):
    # Bad first names
    for data in [{'firstName': ' Han', 'lastName': 'Solo'}, {'firstName': 'Han ', 'lastName': 'Solo'},
                 {'firstName': 'H an', 'lastName': 'Solo'}]:

        with client.session_transaction() as sess:
            sess['user'] = mock_user('hsolo@gmail.com', False)
        res = client.post('/newuser', data=data, follow_redirects=True)
        assert b'Please enter your name below' in res.data
        assert space_in_first_name_error.encode('utf-8') in res.data
    # Bad last names
    for data in [{'firstName': 'Han', 'lastName': ' Solo'}, {'firstName': 'Han', 'lastName': 'Solo '},
                 {'firstName': 'Han', 'lastName': 'So lo'}]:

        with client.session_transaction() as sess:
            sess['user'] = mock_user('hsolo@gmail.com', False)
        res = client.post('/newuser', data=data, follow_redirects=True)
        assert b'Please enter your name below' in res.data
        assert space_in_last_name_error.encode('utf-8') in res.data

def test_bad_cas_user(client):
    # Bad first names
    for data in [{'firstName': ' Han', 'lastName': 'Solo'}, {'firstName': 'Han ', 'lastName': 'Solo'},
                 {'firstName': 'H an', 'lastName': 'Solo'}]:

        with client.session_transaction() as sess:
            sess['user'] = mock_user('hsolo@gmail.com', False)
        crowdsorting.routes.cas = mock_cas('hsolo')
        res = client.post('/newcasuser', data=data, follow_redirects=True)
        assert b'Please enter your name below' in res.data
        assert space_in_first_name_error.encode('utf-8') in res.data
    # Bad last names
    for data in [{'firstName': 'Han', 'lastName': ' Solo'}, {'firstName': 'Han', 'lastName': 'Solo '},
                 {'firstName': 'Han', 'lastName': 'So lo'}]:

        with client.session_transaction() as sess:
            sess['user'] = mock_user('hsolo@gmail.com', False)
        crowdsorting.routes.cas = mock_cas('hsolo')
        res = client.post('/newcasuser', data=data, follow_redirects=True)
        assert b'Please enter your name below' in res.data
        assert space_in_last_name_error.encode('utf-8') in res.data


