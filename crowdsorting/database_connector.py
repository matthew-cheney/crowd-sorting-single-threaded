from flask_sqlalchemy import SQLAlchemy

class DatabaseConnector():

    @staticmethod
    def connectDatabases(app):
        databases = {}
        databases['russian'] = SQLAlchemy(app)
        databases['english'] = SQLAlchemy(app)
        return databases

    @staticmethod
    def connectModels(app):
        models = {}

        from crowdsorting.db_models.db_base_models import User, Project
        models['base'] = {'User': User, 'Project': Project}


        from crowdsorting.db_models.russian_models import Doc as RDoc
        from crowdsorting.db_models.russian_models import Judge as RJudge
        from crowdsorting.db_models.russian_models import Judgment as RJudgment
        models['russian'] = {'Doc': RDoc, 'Judge': RJudge, 'Judgment': RJudgment}

        from crowdsorting.db_models.english_models import Doc as EDoc
        from crowdsorting.db_models.english_models import Judge as EJudge
        from crowdsorting.db_models.english_models import Judgment as EJudgment
        models['english'] = {'Doc': EDoc, 'Judge': EJudge, 'Judgment': EJudgment}
        return models
