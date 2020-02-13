from flask_testing import TestCase
import unittest

from crowdsorting import create_app, db

class MyTest(TestCase):

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):

        # pass in test configuration
        return create_app(self)

    def setUp(self):

        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

class SomeTest(MyTest):

    def test_something(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
