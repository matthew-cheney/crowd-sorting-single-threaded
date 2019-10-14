from datetime import datetime
from crowdsorting import databases
from flask_login import UserMixin

db = databases['english']
bind_key = 'english'

class Doc(db.Model, UserMixin):
    __bind_key__ = bind_key
    __tablename__ = 'doc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_compares = db.Column(db.Integer, default=0)
    checked_out = db.Column(db.Boolean, default=False)
    contents = db.Column(db.String(100000), default="")

    def __repr__(self):
        return f"\nDoc id={self.id}, name={self.name}, date_added={self.date_added}, num_compares={self.num_compares}"

class Judge(db.Model):
    __bind_key__ = bind_key
    __tablename = 'judge'
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    judgments = db.relationship('Judgment', backref='judger', lazy=True)

    def __repr__(self):
        return f"\nJudge('{self.firstName} {self.lastName}', '{self.username}', '{self.email}')"

class Judgment(db.Model):
    __bind_key__ = bind_key
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

    def __repr__(self):
        return f"\nJudgment(Judge='{self.judge.username}', doc_harder='{self.doc_harder.name}', doc_easier='{self.doc_easier.name}')"
