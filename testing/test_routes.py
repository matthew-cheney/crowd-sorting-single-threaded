import unittest

import crowdsorting

class test_routes(unittest.TestCase):

    def setUp(self):
        crowdsorting.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/test_crowdsorting.db'
        crowdsorting.app.config[
            'PAIRS_BEING_PROCESSED_PATH'] = 'test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()
        self.c = crowdsorting.app.test_client()

    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_home_no_login(self):
        home_return = self.c.get('/home')
        page_content = home_return.data.decode('utf-8')
        self.assertTrue('o use this app, please log in at the upper right corner.' in page_content)

    def test_about_no_login(self):
        about_return = self.c.get('/about')
        page_content = about_return.data.decode('utf-8')
        self.assertTrue('About Crowd Sorting' in page_content)

    def test_no_login_restricted_access(self):
        pass