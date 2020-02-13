import unittest
from time import sleep

import crowdsorting
from crowdsorting.app_resources.DBHandler import DBHandler
from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy
from crowdsorting.app_resources.sorting_algorithms.MonteCarloProxy import MonteCarloProxy
from crowdsorting.database.models import Project, Doc, Judge, Judgment

class New_User(unittest.TestCase):

    def setUp(self):
        crowdsorting.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/_test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = '_test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()



    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_vanilla_user(self):

        pass



class Dummy_User:
    def __init__(self, firstName, lastName, email, username):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.username = username

user1 = Dummy_User('Harry', 'Potter', 'hpotter@gmail.com', 'hp1')
user2 = Dummy_User('Ron', 'Weasley', 'rweasley@gmail.com', 'rw1')
user3 = Dummy_User('Hermione', 'Granger', 'hgranger@gmail.com', 'hg1')
