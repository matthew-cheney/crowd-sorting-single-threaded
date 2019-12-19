from crowdsorting.app_resources.db_classes.Doc import Doc
from crowdsorting.app_resources.db_classes.Judge import Judge
from crowdsorting.app_resources.db_classes.Judgment import Judgment


class ProjectHolder:
    def __init__(self, name):
        self.name = name
        self.Doc = Doc
        self.Judge = Judge
        self.Judgment = Judgment
