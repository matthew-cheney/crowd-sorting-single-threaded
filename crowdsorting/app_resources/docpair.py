from datetime import datetime

class DocPair():

    doc1 = ""
    doc2 = ""
    timestamp = ""
    lifeSeconds = 0

    def __init__(self, doc1, doc2):
        self.doc1 = doc1
        self.doc2 = doc2
        self.timestamp = datetime.now()
        lifeSeconds = 30

    def equals(self, other):
        if self.doc1.id == other.doc1.id and self.doc2.id == other.doc2.id:
            return True
        else:
            return False

    def getFirst(self):
        return self.doc1.name

    def getSecond(self):
        return self.doc2.name

    def getDocOne(self):
        return self.doc1

    def getDocTwo(self):
        return self.doc2

    def getTimestamp(self):
        return self.timestamp

    def __str__(self):
        return f"{self.doc1.name}, {self.doc2.name}, time:{self.timestamp}"

    def getLifeSeconds(self):
        return self.lifeSeconds

    def updateTimestamp(self):
        self.timestamp = datetime.now()

    def getFirstContents(self):
        return self.doc1.contents

    def getSecondContents(self):
        return self.doc2.contents
