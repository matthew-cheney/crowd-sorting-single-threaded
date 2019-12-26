from crowdsorting import session, pairselectors
from crowdsorting import db
from crowdsorting.database.models import Project, Doc, Judge, Judgment
from crowdsorting import models
from datetime import datetime
from datetime import timedelta
import pickle

from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy


class DBHandler:

    def __init__(self):
        self.unpickle_pairs_being_processed()

    def pickle_pairs_being_processed(self):
        with open(f"crowdsorting/app_resources/pairs_being_processed/pairsBeingProcessed.pkl", "wb") as f:
            pickle.dump(self.pairsBeingProcessed, f)

    def unpickle_pairs_being_processed(self):
        try:
            with open(f"crowdsorting/app_resources/pairs_being_processed/pairsBeingProcessed.pkl", "rb") as f:
                self.pairsBeingProcessed = pickle.load(f)
        except FileNotFoundError:
            self.pairsBeingProcessed = {}

    def db_file_names(self, project):
        filesInDatabase = db.session.query(Doc).filter_by(
            project_name=project).all()
        filenamesInDatabase = []
        for file in filesInDatabase:
            filenamesInDatabase.append(file.name)
        return filenamesInDatabase

    # Function to add new files to db
    def add_docs(self, validFiles, project):
        print("in addDocs function")
        filenamesInDatabase = self.db_file_names(project)
        newFile = False
        for file in validFiles:
            if not file.filename in filenamesInDatabase:
                print(f"{file} is not in the databse yet")
                self.create_doc(file.filename, file.read(), project)
                newFile = True
        if newFile:
            db.session.commit()

    def add_pairs_being_processed(self, project):
        self.pairsBeingProcessed[project] = []
        self.pickle_pairs_being_processed()

    # Function to get next pair of docs
    def get_pair(self, project):
        self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            self.add_pairs_being_processed(project)
        for pair in self.pairsBeingProcessed[project]:
            if (pair.get_timestamp() < (datetime.now() - timedelta(seconds=30))) or \
                    (pair.checked_out == False):
                pair.update_time_stamp()
                print(f"pair timestamp set to {pair.get_timestamp()}")
                print(f"serving stored pair {pair}")
                pair.checked_out = True
                self.pickle_pairs_being_processed()
                return pair
        allDocs = db.session.query(Doc).filter_by(project_name=project,
                                                  checked_out=False).all()
        allJudgments = db.session.query(Judgment).filter_by(
            project_name=project).all()
        print('allJudgments:', allJudgments)
        pair = pairselectors[project].get_pair(len(allDocs), allDocs)
        if not pair:
            return pair
        if type(pair) == type(""):
            print(pair)
            print('no more pairs')
            return pair
        self.pairsBeingProcessed[project].append(pair)
        self.pickle_pairs_being_processed()
        doc1 = db.session.query(Doc).filter_by(name=pair.get_first(),
                                               project_name=project).first()
        doc2 = db.session.query(Doc).filter_by(name=pair.get_second(),
                                               project_name=project).first()
        doc1.checked_out = True
        doc2.checked_out = True
        db.session.commit()
        for pair in self.pairsBeingProcessed[project]:
            print(pair)
        return pair

    # Function to create new judgment
    def create_judgment(self, harder, easier, project, judge):
        print(f"The winner is {harder}")
        print(f"The loser is {easier}")
        harder_doc = \
            db.session.query(Doc).filter_by(name=harder,
                                            project_name=project).first()
        easier_doc = \
            db.session.query(Doc).filter_by(name=easier,
                                            project_name=project).first()
        harder_doc.checked_out = False
        easier_doc.checked_out = False
        harder_doc.num_compares += 1
        easier_doc.num_compares += 1
        judge_id = session['user'].get_judge_id()
        db.session.add(
            Judgment(doc_harder_id=harder_doc.id, doc_easier_id=easier_doc.id,
                     judge_id=judge_id, project_name=project))
        db.session.commit()
        pairselectors[project].make_judgment(easier_doc, harder_doc,
                                             judge.username)
        self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            self.add_pairs_being_processed(project)
        for pair in self.pairsBeingProcessed[project]:
            if (pair.doc1.name == harder and pair.doc2.name == easier) or (
                    pair.doc1.name == easier and pair.doc2.name == harder):
                self.pairsBeingProcessed[project].remove(pair)
                break
        self.pickle_pairs_being_processed()

    # Function to delete Doc and Judgments from database
    def delete_file(self, name, project):
        for j in db.session.query(Judgment).filter_by(
                project_name=project).all():
            if j.doc_harder.name == name:
                db.session.query(Judgment).filter_by(id=j.id).delete()
                continue
            if j.doc_easier.name == name:
                db.session.query(Judgment).filter_by(id=j.id).delete()

        db.session.query(Doc).filter_by(name=name,
                                        project_name=project).delete()
        db.session.commit()

    def create_doc(self, filename, contents, project):
        doc1 = Doc(name=filename, contents=contents, project_name=project)
        db.session.add(doc1)
        db.session.commit()

    def get_judge(self, judge_username, project):
        allJudges = db.session.query(Judge).all()
        for judge in allJudges:
            if judge.username == judge_username:
                return judge.id
        return "Judge not found"

    def get_user(self, user_username):
        user = db.session.query(Judge).filter_by(
            username=user_username).first()
        if (user is not None):
            return user.id
        return "User not found"

    def get_username(self, user_id):
        user = db.session.query(Judge).filter_by(
            id=user_id).first()
        if (user is not None):
            return user.firstName, user.lastName
        return "User not found"

    def create_user(self, firstName, lastName, judge_username, email):
        db.session.add(Judge(firstName=firstName, lastName=lastName,
                             username=judge_username, email=email))
        db.session.commit()
        return

    def create_judge(self, firstName, lastName, judge_username, email,
                     project):
        db.session.add(Judge(firstName=firstName, lastName=lastName,
                             username=judge_username, email=email))
        db.session.commit()
        return

    def get_number_of_judgments(self, project):
        return pairselectors[project].get_number_comparisons_made()

    def get_number_of_docs(self, project):
        allDocs = db.session.query(Doc).filter_by(project_name=project).all()
        return len(allDocs)

    def get_sorted(self, project):
        allDocs = db.session.query(Doc).filter_by(project_name=project).all()
        allJudgments = db.session.query(Judgment).filter_by(
            project_name=project).all()
        sortedFiles = pairselectors[project].get_sorted(allDocs, allJudgments)
        confidence = pairselectors[project].get_confidence()
        return sortedFiles, confidence

    def get_user_projects(self, user):
        # return self.allProjects() # This is a temporary fix
        projects = db.session.query(Judge).filter_by(
            username=user).first().projects
        # projects = [p.name for p in projects]
        print("projects:", projects)
        return projects

    def get_all_projects(self):
        projects = []
        for p in db.session.query(Project).all():
            projects.append(
                models.Project(models.Project, p.name, p.date_created,
                               p.judges, p.docs, p.judgments))
        return projects

    def create_project(self, project_name, selector_algorithm):
        try:
            print(selector_algorithm)
            print(ACJProxy)
            new_sorter = selector_algorithm(project_name)
            pairselectors[project_name] = new_sorter
            project = Project(name=project_name)
            db.session.add(project)
            db.session.commit()
            message = f"project {project_name} successfully created"
            return message
        except Exception:
            print(Exception)
            message = "unable to create project"
        return message

    def get_possible_judgments_count(self, project):
        return pairselectors[project].get_possible_judgments_count()

    def get_email(self, userID):
        user = db.session.query(Judge).filter_by(
            id=userID).first()
        if (user is not None):
            return user.email
        return "User not found"

    def get_all_users(self):
        users = db.session.query(Judge).all()
        return users

    def add_user_to_project(self, userId, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        user = db.session.query(Judge).filter_by(id=userId).first()
        project.judges.append(user)
        db.session.commit()

    def remove_user_from_project(self, userId, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        user = db.session.query(Judge).filter_by(id=userId).first()
        project.judges.remove(user)
        db.session.commit()

    def update_user_info(self, newFirstName, newLastName, username, newEmail):
        user = db.session.query(Judge).filter_by(username=username).first()
        user.firstName = newFirstName
        user.lastName = newLastName
        user.email = newEmail
        db.session.commit()

    def return_pair(self, pair, project):
        self.unpickle_pairs_being_processed()
        for out_pair in self.pairsBeingProcessed[project]:
            if (pair[0] == out_pair.doc1.name and pair[1] == out_pair.doc2.name) or \
               (pair[1] == out_pair.doc1.name and pair[0] == out_pair.doc2.name):
                out_pair.checked_out = False
                self.pickle_pairs_being_processed()
                return
        print("pair not found in pairsBeingProcessed")
