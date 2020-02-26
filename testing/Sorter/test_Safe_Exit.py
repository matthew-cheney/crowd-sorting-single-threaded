import unittest
from time import sleep
import os
import re

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

        # Find which two docs were served
        doc1, doc2 = extract_docs(res.data.decode('utf-8'))
        self.assertTrue(doc1.endswith('.txt'))
        self.assertTrue(doc2.endswith('.txt'))

        # Safe Exit
        res = self.client.post('/safeexit', data={
            'file_one_name': doc1,
            'file_two_name': doc2
        }, follow_redirects=True)
        self.assertTrue(DEFAULT_LANDING_PAGE.encode('utf-8') in res.data)

        # Go to sorter again
        res = self.client.get('/sorter', follow_redirects=True)
        self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

        # Check if got same docs back
        doc1_new, doc2_new = extract_docs(res.data.decode('utf-8'))
        self.assertTrue(doc1 in [doc1_new, doc2_new])
        self.assertTrue(doc2 in [doc1_new, doc2_new])

        # Delete project
        self.assertTrue(os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))
        self.client.post('/deleteProject', data={'project_name_delete': project_name}, follow_redirects=True)
        self.assertFalse(os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))
