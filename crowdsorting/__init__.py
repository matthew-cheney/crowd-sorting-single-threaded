import pickle
from glob import glob

from flask import Flask, session
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from oauthlib.oauth2 import WebApplicationClient

from crowdsorting.app_resources.yamlReader import yamlReader
import os

from flask_cas import CAS

from crowdsorting.models.User import User

app = Flask(__name__)

yamlReader.readConfig("config.yaml", app)

cas = CAS(app, '/cas')

login_manager = LoginManager()
login_manager.init_app(app)


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

"""@login_manager.user_loader
def load_user(user_id):
    print("in __init__ load_user", user_id)
    return User.username"""

app.secret_key = '398247b108570892173509827389057'
Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from crowdsorting.database.models import Project, Doc, Judge, Vote, Judgment
from crowdsorting.app_resources.sorting_algorithms.selectionalgorithm import SelectionAlgorithm
from crowdsorting.app_resources.sorting_algorithms.ACJProxy import ACJProxy
from crowdsorting.app_resources.sorting_algorithms.MonteCarloProxy import MonteCarloProxy


pairselector_options = list()
pairselector_options.append(ACJProxy)
pairselector_options.append(MonteCarloProxy)


pairselectors = dict()
instance_filenames = glob('crowdsorting/app_resources/sorter_instances/*.pkl')
if len(instance_filenames) > 0:
    for file in instance_filenames:
        pairselectors[os.path.basename(file)[:-4]] = pickle.load(open(file, 'rb'))


# from crowdsorting.app_resources.AdminModelView import *
from crowdsorting.app_resources import routes

"""admin = Admin(app, name='sorter', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(ProjectView(Project, db.session))
admin.add_view(DocView(Doc, db.session))
admin.add_view(JudgeView(Judge, db.session))
admin.add_view(VoteView(Vote, db.session))
admin.add_view(JudgmentView(Judgment, db.session))
"""