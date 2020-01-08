class Project(object):

    def __init__(self, name, sorting_algorithm, date_created, judges, docs, judgments):
        self.name = name
        self.sorting_algorithm = sorting_algorithm
        self.date_created = date_created
        self.judges = judges
        self.docs = docs
        self.judgments = judgments

    def __repr__(self):
        return f"Name: {self.name}; alg: {self.sorting_algorithm}"
