import crowdsorting


def login(client, email):
    return crowdsorting.routes.load_user(email)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_user(client, firstName, lastName, email=None, username=None):
    data = {
            'firstName': firstName,
            'lastName': lastName
    }
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

class mock_user():
    def __init__(self, email, is_authenticated):
        self.email = email
        self.is_authenicated = is_authenticated

    def get_is_authenticated(self):
        return self.is_authenicated

class mock_cas():
    def __init__(self, username):
        self.username = username
