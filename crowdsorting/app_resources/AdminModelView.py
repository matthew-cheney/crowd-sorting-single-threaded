import flask_admin as admin
from flask_admin.contrib import sqla
from crowdsorting import session
from flask_admin import helpers, expose
from flask import url_for
from flask import redirect


class AdminModelView(sqla.ModelView):

    def is_accessible(self):
        print(f"sending back {session['user'].get_is_admin()}")
        return session['user'].get_is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))

class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if 'user' not in session or not session['user'].get_is_admin():
            return redirect(url_for('home'))
        return super(MyAdminIndexView, self).index()
