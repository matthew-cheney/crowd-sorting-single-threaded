import unittest
from time import sleep

import crowdsorting
from crowdsorting.app_resources.DBHandler import DBHandler


class Create_Delete_Docs(unittest.TestCase):

    def setUp(self):
        crowdsorting.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///_test_crowdsorting.db'
        crowdsorting.app.config['PAIRS_BEING_PROCESSED_PATH'] = '_test_pairsbeingprocessed.pkl'
        crowdsorting.db.create_all()
        self.dbhandler = DBHandler()
        self.doc1 = DB_Doc("doc_1.txt", "one one one", "Numbers")
        self.doc2 = DB_Doc("doc_2.txt", "two two two", "Numbers")
        self.doc3 = DB_Doc("doc_3.txt", "three three three", "Numbers")

    def tearDown(self):
        crowdsorting.db.drop_all()


    def test_create_doc_single(self):
        self.dbhandler.create_doc(self.doc1.filename, self.doc1.contents, self.doc1.project)
        return_doc = self.dbhandler.get_doc(self.doc1.filename)
        self.assertEqual(self.doc1.filename, return_doc.name)
        self.assertEqual(self.doc1.contents, return_doc.contents)
        self.assertEqual(self.doc1.project, return_doc.project_name)

    def test_create_doc_multiple(self):
        self.dbhandler.create_doc(self.doc1.filename, self.doc1.contents, self.doc1.project)
        self.dbhandler.create_doc(self.doc2.filename, self.doc2.contents, self.doc2.project)
        self.dbhandler.create_doc(self.doc3.filename, self.doc3.contents, self.doc3.project)

        return_1 = self.dbhandler.get_doc(self.doc1.filename)
        return_2 = self.dbhandler.get_doc(self.doc2.filename)
        return_3 = self.dbhandler.get_doc(self.doc3.filename)

        self.assertEqual(self.doc1.filename, return_1.name)
        self.assertEqual(self.doc1.contents, return_1.contents)
        self.assertEqual(self.doc1.project, return_1.project_name)

        self.assertEqual(self.doc2.filename, return_2.name)
        self.assertEqual(self.doc2.contents, return_2.contents)
        self.assertEqual(self.doc2.project, return_2.project_name)

        self.assertEqual(self.doc3.filename, return_3.name)
        self.assertEqual(self.doc3.contents, return_3.contents)
        self.assertEqual(self.doc3.project, return_3.project_name)

    def test_create_doc_repeat(self):
        self.dbhandler.create_doc(self.doc1.filename, self.doc1.contents, self.doc1.project)
        first_timestamp = self.dbhandler.get_doc(self.doc1.filename).date_added
        sleep(2)
        self.dbhandler.create_doc(self.doc1.filename, self.doc1.contents, self.doc1.project)
        second_timestamp = self.dbhandler.get_doc(self.doc1.filename).date_added
        self.assertEqual(first_timestamp, second_timestamp)

    def test_create_doc_repeat_name(self):
        self.dbhandler.create_doc(self.doc1.filename, self.doc1.contents,
                                  self.doc1.project)
        self.dbhandler.create_doc(self.doc1.filename, self.doc2.contents,
                                  self.doc1.project)
        return_1 = self.dbhandler.get_doc(self.doc1.filename)
        self.assertEqual(self.doc1.contents, return_1.contents)

    def test_add_docs(self):
        filenames = ['../dummy_files/00.txt',
                     '../dummy_files/01.txt',
                     '../dummy_files/02.txt',
                     '../dummy_files/03.txt',
                     '../dummy_files/04.txt',
                     '../dummy_files/05.txt',
                     '../dummy_files/06.txt',
                     '../dummy_files/07.txt',
                     '../dummy_files/08.txt',
                     '../dummy_files/09.txt',
                     '../dummy_files/10.txt']
        files = [Upload_file(filename, open(filename, 'r')) for filename in filenames]

        self.dbhandler.add_docs(files, "temp")

        for file in files:
            return_doc = self.dbhandler.get_doc(file.filename)
            self.assertEqual(file.filename, return_doc.name)
            self.assertEqual(file.contents, return_doc.contents)

        for file in files:
            file.close()


class DB_Doc:
    def __init__(self, filename, contents, project):
        self.filename = filename
        self.contents = contents
        self.project = project

class Upload_file:
    def __init__(self, filename, file):
        self.filename = filename
        self.file = file
        self.contents = file.read()

    def read(self):
        return self.contents

    def close(self):
        self.file.close()