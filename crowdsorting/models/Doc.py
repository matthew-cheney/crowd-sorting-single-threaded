from datetime import datetime

class Doc:
    # __slots__ = ['id']

    def __init__(self, id, name, date_added, num_compares, checked_out, contents, project_id):
        self.id = id
        self.name = name
        self.date_added = date_added
        self.num_compares = num_compares
        self.checked_out = checked_out
        self.contents = contents
        self.project_id = project_id
