from math import floor

import requests
from flask_login import login_user, logout_user

from crowdsorting.app_resources.DBHandler import DBHandler
from crowdsorting import app, cas, session, pairselectors, \
    pairselector_options, GOOGLE_DISCOVERY_URL, client, login_manager, \
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from flask import abort
from flask import flash, send_file
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import make_response
import os

from . import Strings_List as StringList
from .RejectLogger import RejectLogger
from .settings import ADMIN_PATH, PM_PATH, DEFAULT_LANDING_PAGE
from .user import User
import json
import re
import time

from functools import wraps

from crowdsorting.app_resources.forms import NewUserForm, NewProjectForm
from flask_cas import login as cas_login

import datetime

dbhandler = DBHandler()
rejectLogger = RejectLogger()

dummyUser = User("", False, False, 0, "", "", "")


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("checking login ..............................................................")
        try:
            if not dbhandler.check_user(session['user'].email):
                print("someone trying to get in!")
                del session['user']
                return "This page is only accessible to users", 403
            else:
                print("you're ok")
                return fn(*args, **kwargs)
        except KeyError:
            return "This page is only accessible to users", 403
    return wrapper


# @login_manager.user_loader
def load_user(email):
    print('In the login route!')
    # username = user.username
    print("user:", email)
    user_id = dbhandler.get_user(email)
    print("userID", user_id)
    if type(user_id) == type(""):
        print("new user detected")
        session['user'] = User(False, False,
                               False, "", "",
                               "", email)
        return redirect(url_for('newuser'))
    else:
        return returninguser(email, user_id)


def load_cas_user(username):
    print('In the login route!')
    # username = user.username
    print("cas_user:", username)
    user_id = dbhandler.get_cas_user(username)
    print("userID", user_id)
    if type(user_id) == type(""):
        print("new user detected")
        session['user'] = User(False, False,
                               False, "", "",
                               "", "")
        return redirect(url_for('newcasuser'))  # newcasuser()  # Login with CAS - work on this next
    else:
        email = dbhandler.get_cas_email(username)
        return returninguser(email, user_id)


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    if 'user' in session and session['user'].get_is_authenticated():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('home'))
        # Validate first/last names
        first_name = request.form.get('firstName')
        if ' ' in first_name:
            flash(StringList.space_in_first_name_error, 'danger')
            return redirect(url_for('newuser'))
        last_name = request.form.get('lastName')
        if ' ' in last_name:
            flash(StringList.space_in_last_name_error, 'danger')
            return redirect(url_for('newuser'))
        current_user = session['user']  # Need to add user to session before this
        dbhandler.create_user(request.form.get('firstName'), request.form.get('lastName'),
                              current_user.email, None)
        session['user'] = User(True, isInAdminFile(current_user.email),
                               isInPMFile(current_user.email), dbhandler.get_user(current_user.email), request.form.get('firstName'),
                               request.form.get('lastName'), current_user.email)
        print("admin:", session["user"].email, session['user'].is_admin)
        return postLoadUser()
    if request.method == 'POST':
        flash('Failed to register user', 'danger')
    return render_template('newuser.html', current_user=dummyUser, title='New User')


@app.route('/newcasuser', methods=['GET', 'POST'])
def newcasuser():
    if 'user' in session and session['user'].get_is_authenticated():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('home'))
        # Validate first/last names
        first_name = request.form.get('firstName')
        if ' ' in first_name:
            flash(StringList.space_in_first_name_error, 'danger')
            return redirect(url_for('newcasuser'))
        last_name = request.form.get('lastName')
        if ' ' in last_name:
            flash(StringList.space_in_last_name_error, 'danger')
            return redirect(url_for('newcasuser'))
        current_user = session['user']  # Need to add user to session before this
        print("creating cas user for", cas.username)
        if not dbhandler.create_cas_user(request.form.get('firstName'), request.form.get('lastName'),
                              cas.username + '@byu.edu', cas.username):
            flash('Email already taken', 'danger')
            return render_template('newcasuser.html', current_user=dummyUser, title='New User')
        session['user'] = User(True, isInAdminFile(current_user.email),
                               isInPMFile(current_user.email), dbhandler.get_user(cas.username + '@byu.edu'), request.form.get('firstName'),
                               request.form.get('lastName'), cas.username + '@byu.edu')
        print("admin:", session["user"].email, session['user'].is_admin)
        return postLoadUser()
    return render_template('newcasuser.html', current_user=dummyUser, title='New User')



def returninguser(email, user_id):
    admins = []
    db_user_id = dbhandler.get_user(email)
    firstName, lastName = dbhandler.get_user_full_name(db_user_id)
    email = dbhandler.get_email(db_user_id)
    session['user'] = User(True, isInAdminFile(email),
                           isInPMFile(email), user_id, firstName,
                           lastName, email)
    return postLoadUser()

def postLoadUser():
    return redirect(url_for('dashboard'))


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        # picture = userinfo_response.json()["picture"]
        # users_name = userinfo_response.json()["given_name"]  # or family_name

    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        False, False, False, 0, "", "", ""
    )

    # Begin user session by logging the user in
    return load_user(users_email)


@app.route("/logout_master")
@login_required
def logout_master():
    print("in logout()")
    email = ""
    if 'user' in session:
        email = session['user'].email
        session.pop('user', None)
    if email.endswith("@gmail.com"):  # Google user
        logout_user()
    elif email.endswith("@byu.edu"): # CAS user
        return redirect(url_for("cas.logout"))
    return redirect(url_for("home"))


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not isAdmin():
            return "This page is only accessible to administrators", 403
        else:
            return fn(*args, **kwargs)
    return wrapper


@app.route("/cas_login")
def cas_login(other_dest=""):
    print('In the login route!')
    print(cas.username)
    return load_cas_user(cas.username)

    """user_id = dbhandler.get_user(cas.username)
    if type(user_id) == type(""):
        return redirect(url_for('newuser'))
    admins = []

    db_user_id = dbhandler.get_user(cas.username)
    firstName, lastName = dbhandler.get_user_full_name(db_user_id)
    email = dbhandler.get_email(db_user_id)
    session['user'] = User(cas.username, True, isInAdminFile(cas.username), isInPMFile(cas.username), user_id, firstName,
                           lastName, email)
    if other_dest == "":
        return redirect(url_for('projectsdashboard'))
    else:
        return redirect(url_for(other_dest))"""

def isInAdminFile(email):
    with open(ADMIN_PATH, mode='r') as f:
        admins = f.read().split('\n')
    adminBool = False
    for admin in admins:
        if admin == email:
            adminBool = True
            break
    if adminBool:
        userID = dbhandler.get_user_id(email)
        for project in dbhandler.get_all_projects():
            dbhandler.add_user_to_project(userID,
                                          project.name)
    return adminBool

def isInPMFile(email):
    with open(PM_PATH, mode='r') as f:
        pms = f.read().split('\n')
    pmBool = False
    for pm in pms:
        if pm == email:
            pmBool = True
            break
    return pmBool

def isAdmin():
    if not 'user' in session:
        return False
    if not isinstance(session['user'], User):
        return False
    return session['user'].is_admin


@app.route('/old_logout')
def _logout_old():
    print("in old logout")
    session.clear()
    return redirect(url_for('cas.logout'))


@app.route("/dashboard")
def dashboard():
    if 'user' in session and session[
            'user'].get_is_admin():  # This is bad - fix it
        print("returning admindashboard")
        userID = dbhandler.get_user_id(session['user'].email)
        for project in dbhandler.get_all_projects():
            dbhandler.add_user_to_project(userID,
                                          project.name)
        return render_template('admindashboard.html', title='Dashboard',
                               current_user=session['user'],
                               all_users=dbhandler.get_all_users(),
                               selector_algorithms=pairselector_options,
                               all_group_projects=get_all_group_projects(),
                               all_projects=get_all_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project()
                               )
    elif 'user' in session and session['user'].is_pm:
        return render_template('userdashboard.html', title='Dashboard',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project(),
                               StringList=StringList
                               )
    elif 'user' in session:
        all_projects = get_all_user_projects()
        all_public_projects = dbhandler.get_public_projects()
        filtered_public_projects = [x for x in all_public_projects if x not in all_projects]
        return render_template('userdashboard.html', title='Dashbaord',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               current_project=get_current_project(),
                               filtered_public_projects=filtered_public_projects,
                               StringList=StringList
                               )
    else:
        return redirect(url_for('home'))

def get_current_project():
    current_project = request.cookies.get('project')
    if check_current_project(current_project):
        return current_project
    return "select project"

@login_required
def check_current_project(project):
    if 'user' not in session:
        return False
    # all_projects = get_all_group_projects()
    all_projects = dbhandler.get_user_projects(session['user'].email)
    if project not in [x.name for x in all_projects]:
        return False
    return True



def get_all_group_projects():
    if 'user' in session:
        return dbhandler.get_all_group_projects()
    else:
        return []

def get_all_projects():
    return dbhandler.get_all_projects()

def get_all_user_projects():
    if 'user' not in session:
        return []
    return dbhandler.get_user_projects(session['user'].email)

@app.route("/selectproject/<project_name>", methods=["POST"])
@login_required
def selectproject(project_name):
    print("in selectproject with", project_name)
    if project_name == 'None':
        return redirect(url_for('dashboard'))
    if check_select_project(session['user'].email, project_name):
    # response = make_response(redirect(url_for('home')))
        response = make_response()
        response.set_cookie('project', project_name)
        return response
    else:
        return make_response()

@app.route("/addpublicproject", methods=["POST"])
@login_required
def selectpublicproject():
    req_body = request.json
    user_id = dbhandler.get_user_id(req_body['user_email'])
    project_name = req_body['project_name']
    if not user_id:
        return redirect(url_for('home'))
    print("in selectproject with", project_name)
    if project_name == 'None':
        return redirect(url_for('dashboard'))
    dbhandler.add_user_to_project(user_id, project_name)
    response = make_response()
    return response


@app.route("/temp")
@admin_required
def temp():
    return 'temp'

@app.route("/temp_two")
def temp_two():
    print("in temp_two!")
    return 'Hello, World!'


def check_project(current_request):
    if isinstance(current_request.cookies.get('project'), type(None)):
        flash("Please select a project", "warning")
        print("User has not selected project")
        return False
    else:
        project = current_request.cookies.get('project')
        # if dbhandler.project_is_public(project):
        #     return True
        if isAdmin():
            all_projects = dbhandler.get_all_projects()
        else:
            all_projects = dbhandler.get_user_projects(session['user'].email)
        if project not in [x.name for x in all_projects]:
            print("User not given access to project")
            return False
        return True

def check_select_project(user_email, project_name):
    if isAdmin():
        return True
    all_projects = dbhandler.get_user_projects(user_email)
    if project_name in [x.name for x in all_projects]:
        return True
    return False

# Router to home page
@app.route("/")
@app.route("/home")
def home():
    #     if 'user' in Session:
    if 'user' in session:
        if not check_project(request):
            return redirect(url_for('dashboard'))
        current_project = get_current_project()
        return render_template('home.html', title='Home',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=current_project,
                               landing_page=dbhandler.get_landing_page(current_project))
                               # landing_page=DEFAULT_LANDING_PAGE)
    else:
        return render_template('home.html', title='Home',
                               current_user=dummyUser,
                               current_project='',
                               all_projects='',
                               )


#     else:
#         return render_template('home.html', title='Home', current_user=User("", False, False))


# Router to sorting page
@app.route("/sorter")
@login_required
def sorter(admin_docpair=None):
    if 'user' not in session:
        return redirect(url_for('home'))
    if not check_project(request):
        return redirect(url_for('dashboard'))
    if not dbhandler.user_consented(session['user'], request.cookies.get('project')):
        return render_template('consentform.html', title='Consent Form',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project(),
                               consent_form_text=dbhandler.get_consent_form(request.cookies.get('project'))
                               )
    if isinstance(request.cookies.get('project'), type(None)):
        return render_template('nopairs.html', title='Check later',
                               message="No project selected",
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project()
                               )
    try:
        user_email = session['user'].email
        if admin_docpair is None:
            docPair = dbhandler.get_pair(request.cookies.get('project'), user_email)
            admin = False
        else:
            docPair = dbhandler.get_docpair_by_names(admin_docpair[0], admin_docpair[1], request.cookies.get('project'), session['user'].email)
            admin = True
    except KeyError:
        flash('Looks like your selected project has been deleted!', 'warning')
        return redirect(url_for('dashboard'))
    if not docPair:
        flash('Project not ready', 'warning')
        return redirect(url_for('home'))
    if type(docPair) == type(""):
        return render_template('nopairs.html', title='Check later',
                               message=docPair, current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project()
                               )
    try:
        file_one = docPair.get_first_contents().decode("utf-8")
    except AttributeError:
        file_one = docPair.get_first_contents()
    try:
        file_two = docPair.get_second_contents().decode("utf-8")
    except AttributeError:
        file_two = docPair.get_second_contents()

    selection_prompt, preferred_prompt, unpreferred_prompt = dbhandler.get_project_prompts(request.cookies.get('project'))

    return render_template('sorter.html', title='Sorter', file_one=file_one,
                           file_two=file_two,
                           file_one_name=docPair.get_first(),
                           file_two_name=docPair.get_second(),
                           current_user=session['user'],
                           time_started=floor(time.time()),
                           all_projects=get_all_user_projects(),
                           public_projects=dbhandler.get_public_projects(),
                           current_project=get_current_project(),
                           timeout=docPair.lifeSeconds * 1000,
                           selection_prompt=selection_prompt,
                           preferred_prompt=preferred_prompt,
                           unpreferred_prompt=unpreferred_prompt,
                           pair_id=docPair.id,
                           project_name=request.cookies.get('project'),
                           admin=admin
                           )

@app.route("/moretime", methods=['POST'])
@login_required
def moretime():
    req_body = request.json
    pair_id = req_body['pair_id']
    project_name = req_body['project_name']
    dbhandler.reset_timestamp(project_name, pair_id)
    return ""

@app.route("/signconsent", methods=['POST'])
@login_required
def signconsent():
    user_email = request.form.get('user_email')
    current_project = request.form.get('current_project')
    dbhandler.add_consent_judge(user_email, current_project)
    return redirect(url_for('sorter'))

# Router to demo page
@app.route("/demo")
def demo():
    pass

@app.route("/removeself", methods=["POST"])
@login_required
def remove_self_from_project():
    req_body = request.json
    user_id = dbhandler.get_user_id(req_body['user_email'])
    project_name = req_body['project_name']
    if not user_id:
        return redirect(url_for('home'))
    print("in removeself with", project_name)
    if project_name == 'None':
        return make_response()
    dbhandler.remove_user_from_project(user_id, project_name)
    response = make_response()
    response.set_cookie('project', '')
    return response

@app.route("/joincode", methods=["POST"])
@login_required
def join_code():
    project_name = request.form.get("project_name")
    join_code = request.form.get("join_code")
    if dbhandler.check_join_code(project_name, join_code):
        user_id = dbhandler.get_user_id(session['user'].email)
        dbhandler.add_user_to_project(user_id, project_name)
        # flash(f'{project_name} added to My Projects', category='success')
    else:
        pass
        # flash(f'Invalid project name or join code', category='danger')
    return redirect(url_for('dashboard'))


# Router to about page
@app.route("/about", methods=['GET'])
def about():
    if 'user' in session:
        if not check_project(request):
            return redirect(url_for('dashboard'))
        return render_template('about.html', current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project(),
                               title='About'
                               )
    else:
        return render_template('about.html', current_user=dummyUser,
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project(),
                               title='About'
                               )


"""# Router to admin page
@app.route("/myadmin", methods=['GET', 'POST'])
@admin_required
@login_required
def myadmin():
    # if 'user' not in session or not session['user'].get_is_admin():
    # return redirect(url_for('home'))
    # allFiles = [i for i in listdir(app.config['APP_DOCS'])]
    allFiles = []
    return render_template('myadmin.html', title='Admin',
                           allFiles=allFiles, current_user=session['user'])"""


# Router for sorted page
@app.route("/sorted")
@login_required
@admin_required
def sorted():
    if not check_project(request):
        return redirect(url_for('dashboard'))
    if 'user' not in session:
        return redirect(url_for('home'))
    if isinstance(request.cookies.get('project'), type(None)):
        return render_template('nopairs.html', title='Check later',
                               message='No project selected',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project()
                               )
    if dbhandler.get_number_of_docs(request.cookies.get('project')) == 0:
        return render_template('nopairs.html', title='Check later',
                               message='No docs in this project',
                               current_user=session['user'],
                               all_projects=get_all_user_projects(),
                               public_projects=dbhandler.get_public_projects(),
                               current_project=get_current_project()
                               )
    sortedFiles, confidence, *args = dbhandler.get_sorted(
        request.cookies.get('project'))
    confidence = confidence * 100
    confidence = round(confidence, 2)
    number_of_judgments = dbhandler.get_number_of_judgments(
        request.cookies.get('project'))
    number_of_docs = dbhandler.get_number_of_docs(
        request.cookies.get('project'))
    possible_judgments = dbhandler.get_possible_judgments_count(
        request.cookies.get('project'))
    if type(sortedFiles) == type(""):
        success = False
    else:
        success = True
    selection_prompt, preferred_prompt, unpreferred_prompt = dbhandler.get_project_prompts(request.cookies.get('project'))
    return render_template('sorted.html', title='Sorted',
                           sortedFiles=sortedFiles,
                           current_user=session['user'],
                           confidence=confidence,
                           number_of_judgments=number_of_judgments,
                           number_of_docs=number_of_docs,
                           possible_judgments=possible_judgments,
                           success=success,
                           all_projects=get_all_user_projects(),
                           public_projects=dbhandler.get_public_projects(),
                           current_project=get_current_project(),
                           preferred_prompt=preferred_prompt,
                           unpreferred_prompt=unpreferred_prompt
                           )

@app.route("/tower")
@login_required
@admin_required
def tower():
    if not check_project(request):
        return redirect(url_for('dashboard'))
    return render_template('tower.html', current_user=session['user'],
                           all_projects=get_all_user_projects(),
                           public_projects=dbhandler.get_public_projects(),
                           current_project=get_current_project(),
                           roundList=dbhandler.get_round_list(request.cookies.get('project')),
                           pairsCheckedOut=dbhandler.get_pairs_currently_checked_out(request.cookies.get('project')),
                           pairsReadyForRecheckout=dbhandler.get_pairs_waiting_for_recheckout(request.cookies.get('project')),
                           project_proxy=dbhandler.get_proxy(request.cookies.get('project')),
                           active_judges=dbhandler.get_active_judges(request.cookies.get('project'))
                           )

@app.route("/accountinfo", methods=['GET'])
@login_required
def accountinfo():
    return render_template('accountinfo.html', current_user=session['user'],
                           all_projects=get_all_user_projects(),
                           public_projects=dbhandler.get_public_projects(),
                           current_project=get_current_project()
                           )


"""# Delete file route   - This route is obselete?
@app.route("/deleteFile", methods=['POST'])
@login_required
@admin_required
def deleteFile():
    print("in deleteFile route with", request.form.get('id'))
    os.remove((app.config['APP_DOCS'] + '/' + request.form.get('id')))
    dbhandler.delete_file(request.form.get('id'),
                          request.cookies.get('project'))
    return redirect(url_for('myadmin'))"""


"""@app.route("/detectFiles", methods=['POST'])
@login_required
@admin_required
def detectFiles():  # This route is obselete?
    print("in detectFiles route")
    dbhandler.detectFiles(request.cookies.get('project'))
    return redirect(url_for('myadmin'))"""


@app.route("/submitAnswer", methods=['POST'])
@login_required
def submitanswer():
    print("in submitAnswer route")
    if not check_project(request):
        redirect(url_for('home'))
    print(request.form.get("preferred"))
    preferred = request.form.get("preferred")
    not_preferred = ""
    if preferred == request.form.get("file_one_name"):
        not_preferred = request.form.get("file_two_name")
    else:
        not_preferred = request.form.get("file_one_name")
    judge = session['user']
    print(f'judge: {judge.email}')
    if dbhandler.check_user_has_pair([preferred, not_preferred], judge, request.cookies.get('project')):
        time_started = int(request.form.get("time_started"))
        dbhandler.create_judgment(preferred, not_preferred, request.cookies.get('project'),
                                  judge, floor(time.time()) - time_started)
    if request.form.get('admin') == 'True':
        return redirect(url_for('tower'))
    if isinstance(request.form.get('another_pair_checkbox'), type(None)):
        # flash('Judgment submitted', 'success')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('sorter'))

@app.route("/safeexit", methods=['POST'])
@login_required
def safeexit():
    print("in safe exit")
    doc1 = request.form.get('file_one_name')
    doc2 = request.form.get('file_two_name')
    admin = request.form.get('admin')
    project = request.cookies.get('project')
    if dbhandler.check_user_has_pair([doc1, doc2], session['user'], project):
        dbhandler.return_pair((doc1, doc2), project)
    if admin == 'True':
        return redirect(url_for('tower'))
    return redirect(url_for('home'))

@app.route("/hardeasy", methods=['POST'])
@login_required
def hardeasy():
    print(f"in hardeasy for {session['user'].email}")
    doc1 = request.form.get('file_one_name')
    doc2 = request.form.get('file_two_name')
    too_hard = request.form.get('too_hard')
    if too_hard == '1':
        too_hard = True
    else:
        too_hard = False
    project = request.cookies.get('project')
    if dbhandler.check_user_has_pair([doc1, doc2], session['user'], project):
        dbhandler.return_pair((doc1, doc2), project, session['user'].email)
        rejectLogger.log_reject(project, session['user'].email, doc1, doc2, too_hard)
    return redirect(url_for('sorter'))


ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[
        1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['POST'])
@login_required
@admin_required
def uploadFile(files, project):
    # if not check_project(request):
    #     return redirect(url_for('projectsdashboard'))

    validFiles = []
    # if 'file' not in request.files:
    #     return redirect(request.url)
    # files = request.files.getlist("file")
    for file in files:
        if file.filename == '':
            print("No file selected for uploading")
            return "Error: No file selected for uploading"
        if file and allowed_file(file.filename):
            validFiles.append(file)
        else:
            pass
            # flash('Allowed file types are txt', 'danger')
    flash(f'{len(validFiles)} file(s) successfully uploaded', 'success')
    dbhandler.add_docs(validFiles, project)
    filenames = [x.filename for x in files]
    return filenames


@app.route("/addproject", methods=['POST'])
@login_required
@admin_required
def add_project():
    algorithm_to_use = None
    for algorithm in pairselector_options:
        if request.form.get('selector_algorithm') == algorithm.get_algorithm_name():
            algorithm_to_use = algorithm
    message = dbhandler.create_project(request.form.get('project_name'), algorithm_to_use, request.form.get('description'), public=request.form.get('public'), join_code=request.form.get('join_code'))
    print(message)
    if message == "unable to create project":
        flash(message, "warning")
    filenames = uploadFile(request.files.getlist("file"), request.form.get('project_name'))

    pairselectors[request.form.get('project_name')].initialize_selector(
        filenames,
        rounds=15,
        maxRounds=15)

    return redirect(url_for('dashboard'))


@app.route("/addusertoproject", methods=['POST'])
@login_required
@admin_required
def add_user_to_project():
    print(f"in add_user_to_project at {datetime.datetime.now()}")
    req_body = request.json
    if req_body['action'] == 'add':
        print(f"adding {req_body['project']} to {req_body['user']}")
        dbhandler.add_user_to_project(req_body['user'], req_body['project'])
    else:
        print(f"remove {req_body['project']} from {req_body['user']}")
        dbhandler.remove_user_from_project(req_body['user'],
                                           req_body['project'])
    return ""


@app.route("/updateUserInfo", methods=['POST'])
@login_required
def update_user_info():
    newFirstName = request.form.get('firstName')
    newLastName = request.form.get('lastName')

    if newFirstName == "":
        flash("First Name cannot be empty", 'warning')
        return redirect(url_for('accountinfo'))
    if newLastName == "":
        flash("Last Name cannot be empty", "warning")
        return redirect(url_for('accountinfo'))

    email = session['user'].email

    dbhandler.update_user_info(newFirstName, newLastName, email)
    return load_user(email)

@app.route("/editproject", methods=['POST'])
@login_required
@admin_required
def edit_project():
    project = request.form.get('project_name_edit')
    name, description, selection_prompt, preferred_prompt, unpreferred_prompt, consent_form, instruction_page = dbhandler.get_all_project_data(project)
    return render_template('editproject.html', current_user=session['user'],
                           all_projects=get_all_user_projects(),
                           public_projects=dbhandler.get_public_projects(),
                           current_project=get_current_project(),
                           name=name,
                           description=description,
                           selection_prompt=selection_prompt,
                           preferred_prompt=preferred_prompt,
                           unpreferred_prompt=unpreferred_prompt,
                           consent_form=consent_form,
                           instruction_page=instruction_page
                           )

@app.route("/updateprojectinfo", methods=['POST'])
@login_required
@admin_required
def update_project_info():
    name = request.form.get('name')
    description = request.form.get('description')
    selection_prompt = request.form.get('selection_prompt')
    preferred_prompt = request.form.get('preferred_prompt')
    unpreferred_prompt = request.form.get('unpreferred_prompt')
    consent_form = request.form.get('consent_page')
    instruction_page = request.form.get('instruction_page')
    success = dbhandler.update_project_info(name, name, description, selection_prompt, preferred_prompt, unpreferred_prompt, consent_form, instruction_page)
    if success:
        return redirect(url_for('dashboard'))
    else:
        flash('Error editing project')
        return redirect(url_for('dashboard'))

def _json_string_to_dict(json_string):
    return json.loads(json_string)


def check(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if (re.search(regex, email)):
        return True
    else:
        return False

@app.route("/deleteProject", methods=["POST"])
@login_required
@admin_required
def deleteProject():
    # Remove project from database
    dbhandler.delete_project(request.form.get('project_name_delete'))
    rejectLogger.delete_project_logs(request.form.get('project_name_delete'))

    # Remove project from pairs being processed
    # Remove pickled algorithm
    # Remove pickled log files

    return redirect(url_for('dashboard'))

@app.route("/deleteuser", methods=['POST'])
@login_required
@admin_required
def deleteUser():
    dbhandler.delete_user(request.form.get('email'))
    return redirect(url_for('dashboard'))

@app.route("/crowdsorting.db", methods=["GET"])
@login_required
@admin_required
def downloadDatabase():
    try:
        return send_file(
            'database/crowdsorting.db',
            attachment_filename='crowdsorting.db')
    except Exception as e:
        return str(e)

@app.route("/forcereturn", methods=["POST"])
@login_required
@admin_required
def force_return():
    doc_one = request.form.get('doc_one')
    doc_two = request.form.get('doc_two')
    project = request.form.get('project_name')
    user_email = request.form.get('user_email')
    dbhandler.return_pair([doc_one, doc_two], project)
    return redirect(url_for('tower'))

@app.route("/adminsorter", methods=["POST"])
@login_required
@admin_required
def admin_sorter():
    doc_one = request.form.get('doc_one')
    doc_two = request.form.get('doc_two')
    project = request.form.get('project_name')
    return sorter(admin_docpair=[doc_one, doc_two])