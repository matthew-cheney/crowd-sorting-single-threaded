import io
import os
from glob import glob
import re

import crowdsorting


def login(client, email):
    return crowdsorting.routes.load_user(email)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_user(client, firstName, lastName, email=None, username=None, admin=False):
    data = {
            'firstName': firstName,
            'lastName': lastName
    }
    if admin:
        new_admin_path = 'crowdsorting/testing/_admins.txt'
        with open(new_admin_path, 'w') as f:
            f.write(email)
        crowdsorting.routes.ADMIN_PATH = new_admin_path

    if username == None:
        with client.session_transaction() as sess:
            sess['user'] = mock_user(email, False)
        res = client.post('/newuser', data=data, follow_redirects=True)
    else:
        with client.session_transaction() as sess:
            sess['user'] = mock_user(username + '@byu.edu', False)
        crowdsorting.routes.cas = mock_cas(username)
        res = client.post('/newcasuser', data=data, follow_redirects=True)
    return res

def create_project(client, project_name, number_of_docs, selector_algorithm=None, description=None, public=False, join_code=None, src_file_path='testing/dummy_files'):

    if selector_algorithm is None:
        selector_algorithm = 'Adaptive Comparative Judgment'
    if description is None:
        description = ''
    if public:
        public = 'test_True'
    else:
        public = 'test_False'
    if join_code is None:
        join_code = ''

    """
    request.form:
    selector_algorithm
    project_name
    description
    public
    join_code

    request.files
    """

    try:

        fpaths = glob(f'{src_file_path}/*.txt')

        files = [open(fpath, 'rb') for fpath in fpaths[:10]]

        data = {'project_name': project_name,
                'selector_algorithm': selector_algorithm,
                'description': description,
                'public': public,
                'join_code': join_code
                }

        data['file'] = files

        res = client.post('/addproject', data=data, follow_redirects=True)
        return res
    finally:
        for f in files:
            f.close()

def extract_docs(data):
    docs = re.findall('document\.getElementById\("preferred_hidden"\)\.value = "(.*)"', data)
    if len(docs) == 1:
        return docs[0], 'no file'
    if len(docs) == 0:
        return 'no file', 'no file'
    return docs[0], docs[1]

def new_project_to_sorter(client, project_name, firstName, lastName, email, number_of_docs):
    # Set up user and project
    create_user(client, firstName, lastName, email, admin=True)
    create_project(client, project_name, number_of_docs=10)

    # Select project
    res = client.post(f'/selectproject/{project_name}',
                           follow_redirects=True)

    # Open the sorter page
    client.set_cookie('test1', 'project', project_name)
    res = client.get('/sorter', follow_redirects=True)

    # "Press" the agree button and get pair to judge
    data = {
        'user_email': email,
        'current_project': project_name
    }
    res = client.post('/signconsent', data=data, follow_redirects=True)

    return res


class mock_user():
    def __init__(self, email, is_authenticated):
        self.email = email
        self.is_authenicated = is_authenticated

    def get_is_authenticated(self):
        return self.is_authenicated

class mock_cas():
    def __init__(self, username):
        self.username = username

class Dummy_File:
    def __init__(self, filename, file):
        self.filename = filename
        self.file = file
        self.contents = file.read()

    def read(self):
        return self.contents

    def close(self):
        self.file.close()

file1 = Dummy_File('01.txt', open('testing/dummy_files/01.txt', 'r'))
file2 = Dummy_File('02.txt', open('testing/dummy_files/02.txt', 'r'))
file3 = Dummy_File('03.txt', open('testing/dummy_files/03.txt', 'r'))
file4 = Dummy_File('04.txt', open('testing/dummy_files/04.txt', 'r'))
file5 = Dummy_File('05.txt', open('testing/dummy_files/05.txt', 'r'))
file6 = Dummy_File('06.txt', open('testing/dummy_files/06.txt', 'r'))
file7 = Dummy_File('07.txt', open('testing/dummy_files/07.txt', 'r'))
file8 = Dummy_File('08.txt', open('testing/dummy_files/08.txt', 'r'))
file9 = Dummy_File('09.txt', open('testing/dummy_files/09.txt', 'r'))
file10 = Dummy_File('10.txt', open('testing/dummy_files/10.txt', 'r'))
