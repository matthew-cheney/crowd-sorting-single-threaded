import unittest
import time
import os
import re

import crowdsorting
from crowdsorting.app_resources.DBHandler import DBHandler
from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy
from crowdsorting.app_resources.sorting_algorithms.MonteCarloProxy import MonteCarloProxy
from crowdsorting.database.models import Project, Doc, Judge, Judgment
from testing.Sorter.sorter_utils import *
from crowdsorting.app_resources.settings import *


class Too_Hard_Easy(unittest.TestCase):

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

    def test_hard_easy_basic(self):
        project_name = 'test_one'
        firstName = 'Obi-wan'
        lastName = 'Kenobi'
        email = 'dontrememberanydroids@gmail.com'
        try:
            res = new_project_to_sorter(self.client, project_name, firstName, lastName, email, 10)

            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

            # Find which two docs were served
            doc1, doc2 = extract_docs(res.data.decode('utf-8'))
            self.assertTrue(doc1.endswith('.txt'))
            self.assertTrue(doc2.endswith('.txt'))

            # Too hard
            res = self.client.post('/hardeasy', data={
                'file_one_name': doc1,
                'file_two_name': doc2,
                'too_hard_input': 1
            }, follow_redirects=True)
            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

            # Go to sorter again
            res = self.client.get('/sorter', follow_redirects=True)
            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

            # Check if got new docs
            doc1_new, doc2_new = extract_docs(res.data.decode('utf-8'))
            self.assertTrue(doc1 not in [doc1_new, doc2_new])
            self.assertTrue(doc2 not in [doc1_new, doc2_new])

            # Too easy
            doc1 = doc1_new
            doc2 = doc2_new

            res = self.client.post('/hardeasy', data={
                'file_one_name': doc1,
                'file_two_name': doc2,
                'too_hard_input': 0
            }, follow_redirects=True)
            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

            # Go to sorter again
            res = self.client.get('/sorter', follow_redirects=True)
            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

            # Check if got new docs
            doc1_new, doc2_new = extract_docs(res.data.decode('utf-8'))
            self.assertTrue(doc1 not in [doc1_new, doc2_new])
            self.assertTrue(doc2 not in [doc1_new, doc2_new])
        finally:
            # Delete project
            self.assertTrue(os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))
            self.client.post('/deleteProject', data={'project_name_delete': project_name}, follow_redirects=True)
            self.assertFalse(os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))

    def test_pass_all_pairs(self):
        project_name = 'test_one_two'
        firstName = 'Obi-wan'
        lastName = 'Kenobi'
        email = 'dontrememberanydroids@gmail.com'
        number_of_docs = 10
        try:
            res = new_project_to_sorter(self.client, project_name, firstName,
                                        lastName, email, number_of_docs)
            self.assertTrue(DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)
            doc1, doc2 = extract_docs(res.data.decode('utf-8'))
            self.assertTrue(doc1.endswith('.txt'))
            self.assertTrue(doc2.endswith('.txt'))

            for i in range((number_of_docs // 2) - 1):
                # Too hard
                res = self.client.post('/hardeasy', data={
                    'file_one_name': doc1,
                    'file_two_name': doc2,
                    'too_hard_input': 1
                }, follow_redirects=True)
                self.assertTrue(
                    DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

                # Go to sorter again
                # res = self.client.get('/sorter', follow_redirects=True)
                # self.assertTrue(
                #     DEFAULT_SELECTION_PROMPT.encode('utf-8') in res.data)

                # Check if got new docs
                doc1_new, doc2_new = extract_docs(res.data.decode('utf-8'))
                self.assertTrue(doc1 not in [doc1_new, doc2_new])
                self.assertTrue(doc2 not in [doc1_new, doc2_new])

                doc1, doc2 = doc1_new, doc2_new

            res = self.client.post('/hardeasy', data={
                'file_one_name': doc1,
                'file_two_name': doc2,
                'too_hard_input': 1
            }, follow_redirects=True)
            self.assertTrue(
                DEFAULT_SELECTION_PROMPT.encode('utf-8') not in res.data)

            doc1, doc2 = extract_docs(res.data.decode('utf-8'))

            self.assertEqual('no file', doc1)
            self.assertEqual('no file', doc2)

        finally:
            # Delete project
            self.assertTrue(
                os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))
            self.client.post('/deleteProject',
                             data={'project_name_delete': project_name},
                             follow_redirects=True)
            self.assertFalse(
                os.path.isdir(f'crowdsorting/ACJ_Logs/{project_name}'))
