import unittest
from time import sleep

import crowdsorting
from crowdsorting.app_resources.DBHandler import DBHandler
from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy
from crowdsorting.app_resources.sorting_algorithms.MonteCarloProxy import MonteCarloProxy
from crowdsorting.database.models import Project, Doc, Judge, Judgment

class Create_Delete_Projects(unittest.TestCase):

    def setUp(self):
        crowdsorting.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = 'test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()
        self.dbhandler = DBHandler()
        self.user1 = Dummy_User('Harry', 'Potter', 'hpotter@gmail.com', 'hp1')
        self.user2 = Dummy_User('Ron', 'Weasley', 'rweasley@gmail.com', 'rw1')
        self.user3 = Dummy_User('Hermione', 'Granger', 'hgranger@gmail.com', 'hg1')

    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_create_user_basic(self):
        self.dbhandler.create_user(self.user1.firstName, self.user1.lastName,
                                   self.user1.email, self.user1.username)
        return_u1 = crowdsorting.db.session.query(Judge).all()
        self.assertEqual(1, len(return_u1))
        self.assertEqual(self.user1.firstName, return_u1[0].firstName)
        self.assertEqual(self.user1.lastName, return_u1[0].lastName)
        self.assertEqual(self.user1.email, return_u1[0].email)
        self.assertEqual(self.user1.username, return_u1[0].username)

        self.dbhandler.delete_user(self.user1.email)

        return_u2 = crowdsorting.db.session.query(Judge).all()
        self.assertEqual(0, len(return_u2))

    def test_get_user(self):
        self.dbhandler.create_user(self.user1.firstName, self.user1.lastName,
                                   self.user1.email, self.user1.username)
        userID = self.dbhandler.get_user(self.user1.email)
        db_userID = crowdsorting.db.session.query(Judge).filter_by(email=self.user1.email).first().id
        self.assertEqual(db_userID, userID)

class Dummy_User:
    def __init__(self, firstName, lastName, email, username):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.username = username