class User():
    username = ""
    is_authenticated = False
    is_admin = False
    judge_id = 0
    def __init__(self, username, authenticated, admin, judge_id):
        self.username = username
        self.is_authenticated = authenticated
        self.is_admin = admin
        self.judge_id = judge_id

    def get_is_authenticated(self):
        return self.is_authenticated

    def get_username(self):
        return self.username

    def get_is_admin(self):
        return self.is_admin

    def get_judge_id(self):
        return self.judge_id
