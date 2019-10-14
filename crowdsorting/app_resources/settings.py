import os
from crowdsorting import app
from crowdsorting import db

APP_ROOT = app.config['APP_ROOT']
APP_DOCS = app.config['APP_DOCS']
ADMIN_PATH = os.path.join(app.config['APP_ROOT'], 'admins.txt')
