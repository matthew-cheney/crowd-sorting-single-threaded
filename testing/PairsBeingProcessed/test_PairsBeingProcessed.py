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
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/_test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = 'test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()
        self.dbhandler = DBHandler()



    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_project_docs_users(self):
        # Add project and user to db, add files, attach user to project
        self.dbhandler.create_project(project1.project_name, project1.sorting_algorithm)
        self.dbhandler.create_user(user1.firstName, user1.lastName, user1.email, user1.username)
        user1_id = crowdsorting.db.session.query(Judge).first().id
        self.dbhandler.add_user_to_project(user1_id, project1.project_name)

        # Check that project has user listed in db
        project1_db = crowdsorting.db.session.query(Project).filter_by(name=project1.project_name).first()
        self.assertEqual(1, len(project1_db.judges))
        self.assertEqual(user1.firstName, project1_db.judges[0].firstName)
        self.assertEqual(user1.lastName, project1_db.judges[0].lastName)
        self.assertEqual(user1.email, project1_db.judges[0].email)
        self.assertEqual(user1.username, project1_db.judges[0].username)

        # Check that user has project listed in db
        user1_db = crowdsorting.db.session.query(Judge).filter_by(id=user1_id).first()
        self.assertEqual(1, len(user1_db.projects))
        self.assertEqual(project1.project_name, user1_db.projects[0].name)

        # Delete project
        self.dbhandler.delete_project(project1.project_name)

        # Check project no longer in db
        project1_db = crowdsorting.db.session.query(Project).filter_by(name=project1.project_name).first()
        self.assertIsNone(project1_db)

        # Check that user still exists, no attached projects
        user1_db = crowdsorting.db.session.query(Judge).filter_by(id=user1_id).first()
        self.assertEqual(user1.email, user1_db.email)
        self.assertEqual(0, len(user1_db.projects))



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
