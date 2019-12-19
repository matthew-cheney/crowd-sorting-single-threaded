from crowdsorting.models.Doc import Doc


class DatabaseProject:
    def __init__(self, name):
        self.name = name
        self.Doc = Doc
    pass

    class Doc:
        pass

    class Judge:
        pass

    class Judgment:
        pass