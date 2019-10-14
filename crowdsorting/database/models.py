from datetime import datetime
from crowdsorting import db
from sqlalchemy import MetaData, ForeignKey
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import mapper
from crowdsorting.database.database import metadata, db_session

metadata = MetaData()
metadata.bind = db

Judges = db.Table('judges',
    db.Column('project_name', db.String(120), ForeignKey('project.name'), primary_key=True),
    db.Column('judge_id', db.Integer, ForeignKey('judge.id'), primary_key=True)
)


class Project(db.Model):
    __tablename__ = 'project'
    name = db.Column(db.String(120), nullable=False, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    judges = db.relationship('Judge', secondary='judges', lazy='subquery', backref=db.backref('myprojects', lazy=True))
    docs = db.relationship('Doc', cascade='all')
    judgments = db.relationship('Judgment', cascade='all')

    def __repr__(self):
        return f"{self.name}"

    def getName(self):
        return self.name


# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#     firstName = db.Column(db.String(100), nullable=False)
#     lastName = db.Column(db.String(100), nullable=False)
#     username = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#
#     def __repr__(self):
#         return f"\nUser('{self.firstName} {self.lastName}', '{self.username}', '{self.email}')"


class Doc(db.Model, UserMixin):
    __tablename__ = 'doc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_compares = db.Column(db.Integer, default=0)
    checked_out = db.Column(db.Boolean, default=False)
    contents = db.Column(db.String(100000), default="")
    project_name = db.Column(db.String(120), ForeignKey('project.name'))
    judgments_harder = db.relationship('Judgment', foreign_keys='Judgment.doc_harder_id', cascade='all')
    judgments_easier = db.relationship('Judgment', foreign_keys='Judgment.doc_easier_id', cascade='all')

    def __repr__(self):
        return f"\n{self.name}"


class Judge(db.Model):
    __tablename__ = 'judge'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    judgments = db.relationship('Judgment', backref='judger', lazy=True)
    projects = db.relationship('Project', secondary='judges', lazy='subquery', backref=db.backref('myusers', lazy=True))

    def __repr__(self):
        return f"\nJudge('{self.firstName} {self.lastName}', '{self.username}', '{self.email}')"


class Judgment(db.Model):
    __tablename__ = 'judgment'
    id = db.Column(db.Integer, primary_key=True)
    doc_harder_id = db.Column(db.Integer, db.ForeignKey('doc.id'))
    doc_easier_id = db.Column(db.Integer, db.ForeignKey('doc.id'))

    doc_harder = db.relationship('Doc', foreign_keys=[doc_harder_id])
    doc_easier = db.relationship('Doc', foreign_keys=[doc_easier_id])

    # doc_one = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=False)
    # doc_two = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=False)
    # winner = db.Column(db.Integer, db.ForeignKey(Judge.id), nullable=False) # ID of the harder doc
    judge_id = db.Column(db.Integer, db.ForeignKey('judge.id'), nullable=False)

    judge = db.relationship('Judge', foreign_keys=[judge_id])
    project_name = db.Column(db.String(120), ForeignKey('project.name'))

    def __repr__(self):
        return f"\nJudgment(Judge='{self.judge.username}', doc_harder='{self.doc_harder.name}', doc_easier='{self.doc_easier.name}')"



def init_db():
    db.create_all()
