class Project(object):

    def __init__(self, id, name, date_created, judges, docs, judgments):
        self.id = id
        self.name = name
        self.date_created = date_created
        self.judges = judges
        self.docs = docs
        self.judgments = judgments
