from flask import Flask, session
from flask_session import Session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from crowdsorting.app_resources.yamlReader import yamlReader

import os

from flask_cas import CAS

app = Flask(__name__)

yamlReader.readConfig("config.yaml", app)

cas = CAS(app, '/cas')

app.secret_key = '398247b108570892173509827389057'
Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from crowdsorting.db_models.models import Doc, Judge, Judgment
from crowdsorting.app_resources.sorting_algorithms.selection_algorithm import selection_algorithm
from crowdsorting.app_resources.sorting_algorithms.pairall import pairall

pairselector = pairall()

from crowdsorting.app_resources.AdminModelView import *
from crowdsorting.app_resources import routes

admin = Admin(app, name='sorter', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(AdminModelView(Doc, db.session))
admin.add_view(AdminModelView(Judge, db.session))
admin.add_view(AdminModelView(Judgment, db.session))
