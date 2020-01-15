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

    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_create_project_basic(self):
        message = self.dbhandler.create_project('project_one', ACJProxy)
        self.assertEqual(f'project project_one successfully created', message)

        # Check the database directly
        return_p1 = crowdsorting.db.session.query(Project).all()
        self.assertEqual(1, len(return_p1))
        self.assertEqual('project_one', return_p1[0].name)
        self.assertEqual('Adaptive Comparative Judgment', return_p1[0].sorting_algorithm)

    def test_create_project_multiple(self):
        message = self.dbhandler.create_project('project_one', ACJProxy)
        self.assertEqual(f'project project_one successfully created', message)

        message = self.dbhandler.create_project('project_two', MonteCarloProxy)
        self.assertEqual(f'project project_two successfully created', message)

        message = self.dbhandler.create_project('project_three', ACJProxy)
        self.assertEqual(f'project project_three successfully created', message)

        all_projects = crowdsorting.db.session.query(Project).all()
        self.assertEqual(3, len(all_projects))

        return_p1 = crowdsorting.db.session.query(Project).filter_by(name='project_one').all()
        self.assertEqual(1, len(return_p1))
        self.assertEqual('project_one', return_p1[0].name)
        self.assertEqual('Adaptive Comparative Judgment', return_p1[0].sorting_algorithm)

        return_p2 = crowdsorting.db.session.query(Project).filter_by(
            name='project_two').all()
        self.assertEqual(1, len(return_p2))
        self.assertEqual('project_two', return_p2[0].name)
        self.assertEqual('Monte Carlo Sorting',
                         return_p2[0].sorting_algorithm)

        return_p3 = crowdsorting.db.session.query(Project).filter_by(
            name='project_three').all()
        self.assertEqual(1, len(return_p3))
        self.assertEqual('project_three', return_p3[0].name)
        self.assertEqual('Adaptive Comparative Judgment',
                         return_p3[0].sorting_algorithm)

class Dummy_Project:
    def __init__(self, project_name, sorting_algorithm):
        self.project_name = project_name
        self.sorting_algorithm = sorting_algorithm