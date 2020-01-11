class User:
    id = 0
    first_name = ''
    last_name = ''
    email = ''
    projects = []

    def __init__(self, id, first_name, last_name, email, projects):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.projects = projects

    def get_id(self):
        return self.id

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email

    def get_projectS(self):
        return self.projects