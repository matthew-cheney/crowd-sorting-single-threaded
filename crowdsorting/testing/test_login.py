from crowdsorting.testing.utils.testing_utils import login, create_user
from crowdsorting.testing.test_pytest import client
from crowdsorting.app_resources import Strings_List as StringList

def test_vanilla_login(client):
    for email in ['hsolo@gmail.com']:
        res = create_user(client, 'Han', 'Solo', email)
        assert StringList.my_projects.encode('utf-8') in res.data
        assert StringList.no_projects.replace('\'', '&#39;').encode('utf-8') in res.data
        assert email.encode('utf-8') in res.data

        del res

        res = login(client, email)
        assert StringList.my_projects.encode('utf-8') in res.data
        assert StringList.no_projects.replace('\'', '&#39;').encode(
            'utf-8') in res.data
        assert email.encode('utf-8') in res.data


def test_vanilla_cas_login(client):
    res = create_user(client, 'Han', 'Solo', username='hsolo')
    assert StringList.my_projects.encode('utf-8') in res.data
    assert StringList.no_projects.replace('\'', '&#39;').encode('utf-8') in res.data
    assert b'hsolo@byu.edu' in res.data
