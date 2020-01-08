class User():
    username = ""
    is_authenticated = False
    is_admin = False
    judge_id = 0
    def __init__(self, username, authenticated, admin, pm, judge_id, first_name, last_name, email=""):
        self.username = username
        self.is_authenticated = authenticated
        self.is_admin = admin
        self.is_pm = pm
        self.judge_id = judge_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def get_is_authenticated(self):
        return self.is_authenticated

    def get_username(self):
        return self.username

    def get_is_admin(self):
        return self.is_admin

    def get_judge_id(self):
        return self.judge_id

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email
