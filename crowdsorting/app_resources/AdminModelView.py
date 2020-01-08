import flask_admin as admin
from flask_admin.contrib import sqla
from crowdsorting import session
from flask_admin import expose
from flask import url_for
from flask import redirect


class AdminModelView(sqla.ModelView):

    def is_accessible(self):
        # print(f"sending back {session['user'].get_is_admin()}")
        return session['user'].get_is_admin()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home'))


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):
        if 'user' not in session or not session['user'].get_is_admin():
            return redirect(url_for('home'))
        return super(MyAdminIndexView, self).index()


class JudgeView(AdminModelView):
    column_list = ('firstName', 'lastName', 'username', 'email', 'projects')
    column_filters = ['projects.name']
    column_labels = {'projects.name': 'Projects', 'firstName': 'First Name',
                     'lastName': 'Last Name'}


class JudgmentView(AdminModelView):
    column_list = ('id', 'doc_harder', 'doc_easier', 'judge', 'project_name')
    page_size = 50
    column_filters = ['project_name']


class DocView(AdminModelView):
    column_list = (
        'name', 'num_compares', 'checked_out', 'project_name',
        'judgments_harder',
        'judgments_easier')
    column_searchable_list = ['name']
    column_filters = ['project_name']


class ProjectView(AdminModelView):
    column_list = ('name', 'sorting_algorithm', 'date_created', 'judges')


class VoteView(AdminModelView):
    column_list = (
        'id', 'doc_one', 'doc_two', 'doc_one_votes', 'doc_two_votes',
        'resolved',
        'project_name', 'judges')
