from crowdsorting import session, pairselector
from crowdsorting import db
from crowdsorting.database.models import Project, Doc, Judge, Judgment
from crowdsorting import models
from datetime import datetime
from datetime import timedelta

class dbHandler():

    pairsBeingProcessed = {}

    def dbFileNames(self, project):
        filesInDatabase = db.session.query(Doc).filter_by(project_name=project).all()
        filenamesInDatabase = []
        for file in filesInDatabase:
            filenamesInDatabase.append(file.name)
        return filenamesInDatabase

    # Function to add new files to db
    def addDocs(self, validFiles, project):
        print("in addDocs function")
        filenamesInDatabase = self.dbFileNames(project)
        newFile = False
        for file in validFiles:
            if not file.filename in filenamesInDatabase:
                print(f"{file} is not in the databse yet")
                self.createDoc(file.filename, file.read(), project)
                newFile = True
        if newFile:
            db.session.commit()

    def addPairsBeingProcessed(self, project):
        self.pairsBeingProcessed[project] = []

    # Function to get next pair of docs
    def getPair(self, project):
        if project not in self.pairsBeingProcessed:
            self.addPairsBeingProcessed(project)
        for pair in self.pairsBeingProcessed[project]:
            if pair.getTimestamp() < (datetime.now() - timedelta(seconds=30)):
                pair.updateTimestamp()
                print(f"pair timestamp set to {pair.getTimestamp()}")
                print(f"serving stored pair {pair}")
                return pair
        allDocs = db.session.query(Doc).filter_by(project_name=project, checked_out=False).all()
        allJudgments = db.session.query(Judgment).filter_by(project_name=project).all()
        print('allJudgments:', allJudgments)
        # pair = pairselector.getPair(allDocs, allJudgments)
        pair = pairselector.getPair(len(allDocs), allDocs)
        if type(pair) == type(""):
            print('no more pairs')
            return pair
        self.pairsBeingProcessed[project].append(pair)
        doc1 = db.session.query(Doc).filter_by(name=pair.getFirst(), project_name=project).first()
        doc2 = db.session.query(Doc).filter_by(name=pair.getSecond(), project_name=project).first()
        doc1.checked_out = True
        doc2.checked_out = True
        db.session.commit()
        for pair in self.pairsBeingProcessed[project]:
            print(pair)
        return pair

    # Function to create new judgment
    def createJudgment(self, harder, easier, project, judge):
        print(f"The winner is {harder}")
        print(f"The loser is {easier}")
        harder_doc = db.session.query(Doc).filter_by(name=harder, project_name=project).first()
        easier_doc = db.session.query(Doc).filter_by(name=easier, project_name=project).first()
        harder_doc.checked_out = False
        easier_doc.checked_out = False
        harder_doc.num_compares += 1
        easier_doc.num_compares += 1
        judge_id = session['user'].get_judge_id()
        db.session.add(Judgment(doc_harder_id=harder_doc.id, doc_easier_id=easier_doc.id, judge_id=judge_id, project_name=project))
        db.session.commit()
        pairselector.makeJudgment(easier_doc, harder_doc, judge.username)
        if project not in self.pairsBeingProcessed:
            self.addPairsBeingProcessed(project)
        for pair in self.pairsBeingProcessed[project]:
            if (pair.doc1.name == harder and pair.doc2.name == easier) or (pair.doc1.name == easier and pair.doc2.name == harder):
                self.pairsBeingProcessed[project].remove(pair)
                break

    # Function to delete Doc and Judgments from database
    def deleteFile(self, name, project):
        for j in db.session.query(Judgment).filter_by(project_name=project).all():
            if j.doc_harder.name == name:
                db.session.query(Judgment).filter_by(id=j.id).delete()
                continue
            if j.doc_easier.name == name:
                db.session.query(Judgment).filter_by(id=j.id).delete()
            '''
            doc1 = db.session.query(Doc).filter_by(id=j.doc_harder_id).first()
            print('Doc1', doc1)
            doc2 = db.session.query(Doc).filter_by(id=j.doc_easier_id).first()
            print('Doc2', doc2)
            if (type(doc1) == type(Doc()) and doc1.name == name) or (type(doc2) == type(Doc()) and doc2.name == name):
                print('deleting a judgment')
                db.session.query(Judgment).filter_by(id=j.id).delete()
                '''
        db.session.query(Doc).filter_by(name=name, project_name=project).delete()
        db.session.commit()

    def createDoc(self, filename, contents, project):
        doc1 = Doc(name=filename, contents=contents, project_name=project)
        db.session.add(doc1)
        db.session.commit()


    def getJudge(self, judge_username, project):
        allJudges = db.session.query(Judge).all()
        for judge in allJudges:
            if judge.username == judge_username:
                return judge.id
        return "Judge not found"

    def getUser(self, user_username):
        user = db.session.query(Judge).filter_by(username=user_username).first()
        if (user is not None):
            return user.id
        return "User not found"

    def createUser(self, firstName, lastName, judge_username, email):
        db.session.add(Judge(firstName=firstName, lastName=lastName, username=judge_username, email=email))
        db.session.commit()
        return

    def createJudge(self, firstName, lastName, judge_username, email, project):
        db.session.add(Judge(firstName=firstName, lastName=lastName, username=judge_username, email=email))
        db.session.commit()
        return

    def getNumberOfJudgments(self, project):
        return db.session.query(Judgment).count()

    def getNumberOfDocs(self, project):
        return db.session.query(Doc).count()

    def getSorted(self, project):
        allDocs = db.session.query(Doc).filter_by(project_name=project).all()
        allJudgments = db.session.query(Judgment).filter_by(project_name=project).all()
        return pairselector.getSorted(allDocs, allJudgments)

    def getUserProjects(self, user):
        projects = db.session.query(Judge).filter_by(username='mchen95').first().projects
        projects = [p.name for p in projects]
        print("projects:", projects)
        return projects

    def allProjects(self):
        projects = []
        for p in db.session.query(Project).all():
            projects.append(models.Project(models.Project, p.name, p.date_created, p.judges, p.docs, p.judgments))
        return projects

    def createProject(self, project_name):
        try:
            project = Project(name=project_name)
            db.session.add(project)
            db.session.commit()
            message = f"project {project_name} successfully created"
        except:
            message = "unable to create project"
        return message
