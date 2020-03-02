import re
import uuid

from crowdsorting import session, pairselectors
from crowdsorting import db
from crowdsorting.database.models import Project, Doc, Judge, Judgment
from crowdsorting import models
from crowdsorting import app
from datetime import datetime
from datetime import timedelta
import pickle
from crowdsorting.app_resources.settings import *

from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy


class DBHandler:

    def __init__(self):
        self.PBP_Path = app.config['PAIRS_BEING_PROCESSED_PATH']
        self.unpickle_pairs_being_processed()

    def pickle_pairs_being_processed(self):
        with open(self.PBP_Path, "wb") as f:
            pickle.dump(self.pairsBeingProcessed, f)

    def unpickle_pairs_being_processed(self):
        try:
            with open(self.PBP_Path, "rb") as f:
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
                print(f"{file} is not in the database yet")
                self.create_doc(file.filename, file.read(), project)
                newFile = True
        if newFile:
            db.session.commit()

    def add_pairs_being_processed(self, project):
        self.pairsBeingProcessed[project] = []
        self.pickle_pairs_being_processed()

    # Function to get next pair of docs
    def get_pair(self, project, user):
        # self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            self.add_pairs_being_processed(project)
        for pair in self.pairsBeingProcessed[project]:
            if ((pair.get_timestamp() < (datetime.now() - timedelta(seconds=pair.lifeSeconds))) or \
                    (pair.checked_out == False)) and (user not in pair.users_opted_out):
                pair.update_time_stamp()
                print(f"pair timestamp set to {pair.get_timestamp()}")
                print(f"serving stored pair {pair}")
                pair.checked_out = True
                pair.user_checked_out_by = user
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

        if pair.id is None:
            pair.id = uuid.uuid4()

        doc1_contents = re.split(' |\n', pair.doc1.contents.decode('utf-8'))
        doc2_contents = re.split(' |\n', pair.doc2.contents.decode('utf-8'))
        total_length = len(doc1_contents) + len(doc2_contents)
        lifeSeconds = total_length / 2
        pair.lifeSeconds = (lifeSeconds if lifeSeconds > 90 else 90)
        print(f"lifeSeconds: {lifeSeconds}")

        pair.user_checked_out_by = user
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
    def create_judgment(self, harder, easier, project, judge, duration):
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
        pairselectors[project].make_judgment(easier_doc, harder_doc, duration,
                                             judge.email)
        # self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            self.add_pairs_being_processed(project)
        for pair in self.pairsBeingProcessed[project]:
            if (pair.doc1.name == harder and pair.doc2.name == easier) or (
                    pair.doc1.name == easier and pair.doc2.name == harder):
                self.pairsBeingProcessed[project].remove(pair)
                break
        self.pickle_pairs_being_processed()

    def reset_timestamp(self, project_name, pair_id):
        # self.unpickle_pairs_being_processed()
        for each_pair in self.pairsBeingProcessed[project_name]:
            if str(each_pair.id) == pair_id:
                each_pair.update_timestamp()
                self.pickle_pairs_being_processed()
                return True  # Updated timestamp
        self.pickle_pairs_being_processed()
        return False  # Pair not found

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

    def get_doc(self, filename):
        return db.session.query(Doc).filter_by(name=filename).first()

    def get_judge(self, judge_email, project):
        allJudges = db.session.query(Judge).all()
        for judge in allJudges:
            if judge.email == judge_email:
                return judge.id
        return "Judge not found"

    def get_user(self, user_email):
        user = db.session.query(Judge).filter_by(
            email=user_email).first()
        if (user is not None):
            return user.id
        return "User not found"

    def get_cas_user(self, username):
        user = db.session.query(Judge).filter_by(username=username).first()
        if user is not None:
            return user.id
        return "User not found"

    def get_user_full_name(self, user_id):
        user = db.session.query(Judge).filter_by(
            id=user_id).first()
        if (user is not None):
            return user.firstName, user.lastName
        return "User not found"

    def create_user(self, firstName, lastName, email, username):
        db.session.add(Judge(firstName=firstName, lastName=lastName,
                             email=email, username=username))
        db.session.commit()
        return

    def create_cas_user(self, firstName, lastName, email, username):
        # Check if email is already taken
        user = db.session.query(Judge).filter_by(
            email=email).first()
        if user is not None:
            print('no email user:', user)
            return False

        # Email not taken, create user and return true
        db.session.add(Judge(firstName=firstName, lastName=lastName,
                             email=email, username=username))
        db.session.commit()
        return True

    def delete_user(self, email):
        user_to_delete = db.session.query(Judge).filter_by(email=email).first()
        if user_to_delete is None:
            return False
        user_to_delete.projects = []
        user_to_delete.cprojects = []
        db.session.commit()

        user_to_delete = db.session.query(Judge).filter_by(email=email).first()
        if user_to_delete is None:
            return False
        db.session.delete(user_to_delete)
        db.session.commit()
        return True

    def check_user(self, email):
        user = db.session.query(Judge).filter_by(email=email).first()
        if user is None:
            return False
        return True

    def get_cas_email(self, username):
        user = db.session.query(Judge).filter_by(
            username=username).first()
        if (user is not None):
            return user.email
        return "User not found"

    def create_judge(self, firstName, lastName, email,
                     project):
        db.session.add(Judge(firstName=firstName, lastName=lastName,
                             email=email))
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

    def get_user_projects(self, user_email):
        # return self.allProjects() # This is a temporary fix
        try:
            projects = db.session.query(Judge).filter_by(
            email=user_email).first().projects
        except AttributeError:
            return []
        return projects

    def get_public_projects(self):
        projects = db.session.query(Project).filter_by(public=True).all()
        return projects

    def get_all_projects(self):
        projects = []
        for p in db.session.query(Project).all():
            projects.append(
                models.Project(p.name, p.sorting_algorithm, p.date_created,
                               p.judges, p.docs, p.judgments, p.public))
        print("in get_all_projects")
        print(projects)
        if projects is None:
            return []
        return projects

    def get_all_group_projects(self):
        projects = []
        for p in db.session.query(Project).all():
            if not p.public:
                projects.append(
                    models.Project(p.name, p.sorting_algorithm, p.date_created,
                                   p.judges, p.docs, p.judgments, p.public))
        print("in get_all_group_projects")
        print(projects)
        if projects is None:
            return []
        return projects

    def project_is_public(self, project_name):
        project = db.session.query(Project).filter_by(name=project_name).first()
        if project is None:
            return False
        return project.public

    def create_project(self, project_name, selector_algorithm, description=None, selection_prompt=None, preferred_prompt=None, unpreferred_prompt=None, consent_form=None, public=None, landing_page=None, join_code=None):
        if description is None:
            description = DEFAULT_DESCRIPTION
        if public is None:
            public = False
        if public == 'on':
            public = True
        if selection_prompt is None:
            selection_prompt = DEFAULT_SELECTION_PROMPT
        if preferred_prompt is None:
            preferred_prompt = DEFAULT_PREFERRED_PROMPT
        if unpreferred_prompt is None:
            unpreferred_prompt = DEFAULT_UNPREFERRED_PROMPT
        if consent_form is None:
            consent_form = DEFAULT_CONSENT_FORM
        if landing_page is None:
            landing_page = DEFAULT_LANDING_PAGE
        if public == 'test_True':
            public = True
        elif public == 'test_False':
            public = False
        try:
            print(selector_algorithm)
            new_sorter = selector_algorithm(project_name)
            pairselectors[project_name] = new_sorter
            project = Project(name=project_name, sorting_algorithm=selector_algorithm.get_algorithm_name(), description=description, public=public, selection_prompt=selection_prompt, preferred_prompt=preferred_prompt, unpreferred_prompt=unpreferred_prompt, consent_form=consent_form, landing_page=landing_page, join_code=join_code)
            db.session.add(project)
            db.session.commit()
            message = f"project {project_name} successfully created"
            return message
        except Exception:
            print(Exception)
            message = "unable to create project"
        return message

    def get_project_prompts(self, project):
        project_result = db.session.query(Project).filter_by(name=project).first()
        return project_result.selection_prompt, project_result.preferred_prompt, project_result.unpreferred_prompt

    def get_all_project_data(self, project):
        project_result = db.session.query(Project).filter_by(name=project).first()
        return project_result.name, project_result.description, project_result.selection_prompt, project_result.preferred_prompt, project_result.unpreferred_prompt, project_result.consent_form, project_result.landing_page

    def update_project_info(self, project, name, description, selection_prompt, preferred_prompt, unpreferred_prompt, consent_form, instruction_page):
        project_result = db.session.query(Project).filter_by(name=project).first()
        if project_result == None:
            return False
        project_result.name = name
        project_result.description = description
        project_result.selection_prompt = selection_prompt
        project_result.preferred_prompt = preferred_prompt
        project_result.unpreferred_prompt = unpreferred_prompt
        current_consent = project_result.consent_form
        if current_consent != consent_form:
            project_result.cjudges = []
            project_result.consent_form = consent_form
        project_result.landing_page = instruction_page
        db.session.commit()
        return True

    def get_project_users(self, project_name):
        project_result = db.session.query(Project).filter_by(name=project_name).first()
        return project_result.judges

    def get_landing_page(self, project_name):
        project = db.session.query(Project).filter_by(name=project_name).first()
        if project is None:
            return False
        return project.landing_page

    def user_consented(self, user, project):
        project_result = db.session.query(Project).filter_by(name=project).first()
        if project_result is None:
            return False
        if user.email not in [x.email for x in project_result.cjudges]:
            return False
        return True

    def add_consent_judge(self, user_email, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        user = db.session.query(Judge).filter_by(email=user_email).first()
        project.cjudges.append(user)
        db.session.commit()

    def get_consent_form(self, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        if project is None:
            return False
        return project.consent_form

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

    def get_user_id(self, email):
        user = db.session.query(Judge).filter_by(email=email).first()
        if user is None:
            return False
        return user.id

    def add_user_to_project(self, userId, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        user = db.session.query(Judge).filter_by(id=userId).first()
        if user not in project.judges:
            project.judges.append(user)
            db.session.commit()

    def remove_user_from_project(self, userId, projectName):
        project = db.session.query(Project).filter_by(name=projectName).first()
        user = db.session.query(Judge).filter_by(id=userId).first()
        project.judges.remove(user)
        db.session.commit()

    def update_user_info(self, newFirstName, newLastName, email):
        user = db.session.query(Judge).filter_by(email=email).first()
        user.firstName = newFirstName
        user.lastName = newLastName
        db.session.commit()

    def check_join_code(self, project_name, join_code):
        project = db.session.query(Project).filter_by(name=project_name).first()
        if project is None:
            return False
        if project.join_code is None:
            return True
        if project.join_code == join_code:
            return True
        return False

    def return_pair(self, pair, project, user=None):
        # self.unpickle_pairs_being_processed()
        for out_pair in self.pairsBeingProcessed[project]:
            if (pair[0] == out_pair.doc1.name and pair[1] == out_pair.doc2.name) or \
               (pair[1] == out_pair.doc1.name and pair[0] == out_pair.doc2.name):
                out_pair.checked_out = False
                out_pair.user_checked_out_by = None
                if user is not None:
                    out_pair.users_opted_out.append(user)
                self.pickle_pairs_being_processed()
                return
        print("pair not found in pairsBeingProcessed")

    def check_user_has_pair(self, pair, user, project):
        if None in [pair, user, project]:
            return False
        # self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            return False
        for out_pair in self.pairsBeingProcessed[project]:
            if (pair[0] == out_pair.doc1.name and pair[1] == out_pair.doc2.name) or \
                    (pair[1] == out_pair.doc1.name and pair[0] == out_pair.doc2.name):
                if out_pair.user_checked_out_by == user.email:
                    return True
                else:
                    return False
        return False

    def log_rejected_pair(self, pair, project, user=None):
        # self.unpickle_pairs_being_processed()
        pass

    def delete_project(self, project_name):

        # Remove project from pairs_being_processed
        # self.unpickle_pairs_being_processed()
        if project_name in self.pairsBeingProcessed:
            del self.pairsBeingProcessed[project_name]
        self.pickle_pairs_being_processed()

        # Run algorithm delete function

        if project_name in pairselectors:
            pairselectors[project_name].delete_self()

            # Remove algorithm from pairselectors
            del pairselectors[project_name]

        # Remove all judges from project
        project = db.session.query(Project).filter_by(name=project_name).first()
        if project is None:
            return False
        project.judges = []
        project.cjudges = []
        db.session.commit()

        # Delete project
        project = db.session.query(Project).filter_by(name=project_name).first()
        db.session.delete(project)
        db.session.commit()

        return True

    def get_round_list(self, project_name):
        project_proxy = pairselectors[project_name]
        all_round_list = project_proxy.get_round_list()
        return [x for x in all_round_list if x is not None]

    def get_pairs_waiting_for_recheckout(self, project_name):
        # self.unpickle_pairs_being_processed()
        if project_name not in self.pairsBeingProcessed:
            return []
        all_pbp = self.pairsBeingProcessed[project_name]
        filtered_pbp = []
        for pair in all_pbp:
            if ((pair.get_timestamp() < (datetime.now() - timedelta(seconds=pair.lifeSeconds))) or \
                    (pair.checked_out == False)):
                filtered_pbp.append(pair)
        return filtered_pbp

    def get_pairs_currently_checked_out(self, project_name):
        # self.unpickle_pairs_being_processed()
        if project_name not in self.pairsBeingProcessed:
            return []
        all_pbp = self.pairsBeingProcessed[project_name]
        filtered_pbp = []
        for pair in all_pbp:
            if not pair.get_user_checked_out_by() == None:
                filtered_pbp.append(pair)
        return filtered_pbp

    def get_proxy(self, project_name):
        return pairselectors[project_name]

    def get_docpair_by_names(self, doc_one, doc_two, project, user):
        # self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            return 'project not found'
        for pair in self.pairsBeingProcessed[project]:
            if ((doc_one == pair.doc1.name and doc_two == pair.doc2.name) or
                (doc_one == pair.doc2.name and doc_two == pair.doc1.name)):
                pair.update_time_stamp()
                print(f"pair timestamp set to {pair.get_timestamp()}")
                print(f"serving stored pair {pair}")
                pair.checked_out = True
                pair.user_checked_out_by = user
                self.pickle_pairs_being_processed()
                return pair
        return 'pair not found'
    def get_active_judges(self, project):
        # self.unpickle_pairs_being_processed()
        if project not in self.pairsBeingProcessed:
            return []
        judges = set()
        for pair in self.pairsBeingProcessed[project]:
            if pair.checked_out:
                judges.add(pair.user_checked_out_by)
        return judges
