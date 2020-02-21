import unittest
from time import sleep
import os

import crowdsorting
from crowdsorting.app_resources.DBHandler import DBHandler
from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy
from crowdsorting.app_resources.sorting_algorithms.MonteCarloProxy import MonteCarloProxy
from crowdsorting.database.models import Project, Doc, Judge, Judgment
from testing.Sorter.sorter_utils import *
from crowdsorting.app_resources.settings import *


class Safe_Exit(unittest.TestCase):

    def setUp(self):
        crowdsorting.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/_test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = 'test_pairsbeingprocessed.pkl'
        crowdsorting.app.config['TESTING'] = True

        self.dbhandler = DBHandler()

        with crowdsorting.app.test_client() as client:
            with crowdsorting.app.app_context():
                crowdsorting.db.drop_all()
                crowdsorting.db.create_all()
            self.client = client



    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_safe_exit_basic(self):

        project_name = 'test_one'
        firstName = 'Obi-wan'
        lastName = 'Kenobi'
        email = 'dontrememberanydroids@gmail.com'

        # Set up user and project
        create_user(self.client, firstName, lastName, email, admin=True)
        create_project(self.client, project_name, number_of_docs=20)

        # Select project
        res = self.client.post(f'/selectproject/{project_name}', follow_redirects=True)
        self.assertEqual(200, res.status_code)

        # Open the sorter page
        self.client.set_cookie('test1', 'project', project_name)
        res = self.client.get('/sorter', follow_redirects=True)
        self.assertTrue(DEFAULT_CONSENT_FORM.encode('utf-8') in res.data)

        # "Press" the agree button and get pair to judge
        data = {
            'user_email': email,
            'current_project': project_name
        }
        res = self.client.post('/signconsent', data=data, follow_redirects=True)
        self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

        pass


class Dummy_User:
    def __init__(self, firstName, lastName, email, username):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.username = username


class Dummy_Project:
    def __init__(self, project_name, sorting_algorithm):
        self.project_name = project_name
        self.sorting_algorithm = sorting_algorithm

class Dummy_Doc:
    def __init__(self, filename, contents, project):
        self.filename = filename
        self.contents = contents
        self.project = project

class Dummy_File:
    def __init__(self, filename, file):
        self.filename = filename
        self.file = file
        self.contents = file.read()

    def read(self):
        return self.contents

    def close(self):
        self.file.close()

user1 = Dummy_User('Harry', 'Potter', 'hpotter@gmail.com', 'hp1')
user2 = Dummy_User('Ron', 'Weasley', 'rweasley@gmail.com', 'rw1')
user3 = Dummy_User('Hermione', 'Granger', 'hgranger@gmail.com', 'hg1')

project1 = Dummy_Project('Numbers', ACJProxy)
project2 = Dummy_Project('More Numbers', MonteCarloProxy)
