from datetime import datetime
from datetime import timedelta
from math import floor

from crowdsorting.app_resources.settings import DEFAULT_TIMEOUT

class DocPair:
    doc1 = ""
    doc2 = ""
    timestamp = ""
    lifeSeconds = 0

    def __init__(self, doc1, doc2, id=None, lifeSeconds=DEFAULT_TIMEOUT):
        self.doc1 = doc1
        self.doc2 = doc2
        self.timestamp = datetime.now()
        self.lifeSeconds = lifeSeconds
        self.checked_out = True
        self.users_opted_out = list()
        self.id = id
        self.user_checked_out_by = None

    def equals(self, other):
        if self.doc1.id == other.doc1.id and self.doc2.id == other.doc2.id:
            return True
        else:
            return False

    def get_first(self):
        return self.doc1.name

    def get_second(self):
        return self.doc2.name

    def get_doc_one(self):
        return self.doc1

    def get_doc_two(self):
        return self.doc2

    def get_timestamp(self):
        return self.timestamp

    def __str__(self):
        return f"{self.doc1.name}, {self.doc2.name}, time:{self.timestamp}"

    def get_life_seconds(self):
        return self.lifeSeconds

    def update_timestamp(self):
        self.timestamp = datetime.now()

    def update_time_stamp(self):
        self.update_timestamp()

    def get_first_contents(self):
        return self.doc1.contents

    def get_second_contents(self):
        return self.doc2.contents

    def get_user_checked_out_by(self):
        if ((self.get_timestamp() < (
                datetime.now() - timedelta(seconds=self.lifeSeconds)))):
            return None
        else:
            return self.user_checked_out_by

    def get_time_remaining(self):
        all_seconds = self.lifeSeconds - (datetime.now() - self.timestamp).total_seconds()
        minutes = all_seconds / 60
        seconds = (minutes % 1) * 60
        return f'{floor(minutes)} min, {floor(seconds)} sec'