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
            'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testing/test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = 'test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()
        self.dbhandler = DBHandler()



    def tearDown(self):
        crowdsorting.db.drop_all()

    def test_single_project_single_user_judgments(self):
        self.start_single_project(project1, [file1, file2, file3, file4, file5, file6, file7, file8, file9, file10], [user1])
        pair = self.dbhandler.get_pair(project1.project_name)
        self.assertIsNotNone(pair)
        print('pair', pair)


    def start_single_project(self, project, files, users):
        # Add project and user to db, add files, attach user to project
        self.dbhandler.create_project(project.project_name,
                                      project.sorting_algorithm)

        self.dbhandler.add_docs(files, project.project_name)

        for file in files:
            return_doc = self.dbhandler.get_doc(file.filename)
            self.assertEqual(file.filename, return_doc.name)
            self.assertEqual(file.contents, return_doc.contents)

        for user in users:
            self.dbhandler.create_user(user.firstName, user.lastName,
                                       user.email, user.username)
            user_id = crowdsorting.db.session.query(Judge).filter_by(email=user.email).first().id
            self.dbhandler.add_user_to_project(user_id, project1.project_name)


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

file1 = Dummy_File('01.txt', open('../dummy_files/01.txt', 'r'))
file2 = Dummy_File('02.txt', open('../dummy_files/02.txt', 'r'))
file3 = Dummy_File('03.txt', open('../dummy_files/03.txt', 'r'))
file4 = Dummy_File('04.txt', open('../dummy_files/04.txt', 'r'))
file5 = Dummy_File('05.txt', open('../dummy_files/05.txt', 'r'))
file6 = Dummy_File('06.txt', open('../dummy_files/06.txt', 'r'))
file7 = Dummy_File('07.txt', open('../dummy_files/07.txt', 'r'))
file8 = Dummy_File('08.txt', open('../dummy_files/08.txt', 'r'))
file9 = Dummy_File('09.txt', open('../dummy_files/09.txt', 'r'))
file10 = Dummy_File('10.txt', open('../dummy_files/10.txt', 'r'))
