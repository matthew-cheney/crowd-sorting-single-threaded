from crowdsorting.app_resources.dbhandler import dbHandler
from crowdsorting import app, cas, session, pairselector
from flask import flash
from flask import render_template
from flask import url_for
from flask import redirect
from flask import request
from flask import make_response
import os
from .settings import ADMIN_PATH
from .user import User

from crowdsorting.app_resources.forms import NewUserForm, NewProjectForm
from flask_cas import login, logout, login_required

dbhandler = dbHandler()

dummyUser = User("", False, False, 0)

@app.route("/login")
def login():
    print('In the login route!')
    user_id = dbhandler.getUser(cas.username)
    if type(user_id) == type(""):
        return redirect(url_for('newuser'))
    admins = []
    f = open(ADMIN_PATH, mode='r')
    if f.mode == 'r':
        admins = f.read().split('\n')
    f.close()
    adminBool = False
    for admin in admins:
        if admin == cas.username:
            adminBool = True
            break
    session['user'] = User(cas.username, True, adminBool, user_id)

    return redirect(url_for('projectsdashboard'))


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():
    if 'user' in session and session['user'].get_is_authenticated():
        return redirect(url_for('projectsdashboard'))
    form = NewUserForm()
    if form.validate_on_submit():
        dbhandler.createUser(form.firstName.data, form.lastName.data, cas.username, form.email.data)
        return redirect(url_for('login'))
    return render_template('newuser.html', form=form, current_user=dummyUser)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('cas.logout'))

@app.route("/projectsdashboard")
def projectsdashboard():
    if True or 'user' in session and session['user'].get_is_admin():  # This is bad - fix it
        return render_template('admindashboard.html', title='Home', current_user=session['user'], all_projects=dbhandler.allProjects())
    elif 'user' in session:
        return render_template('userdashboard.html', title='Home', current_user=session['user'], all_projects=dbhandler.getUserProjects(session['user'].get_username()))
    else:
        return render_template('userdashboard.html', title='Home', current_user=dummyUser, all_projects=dbhandler.allProjects())

@app.route("/selectproject", methods=["POST"])
def selectproject():
    print(request.form.get('project'))
    if request.form.get('project') == 'None':
        return redirect(url_for('projectsdashboard'))
    response = make_response(redirect(url_for('home')))
    response.set_cookie('project', request.form.get('project'))
    return response

@app.route("/temp")
def temp():
    return 'temp'

# Router to home page
@app.route("/")
@app.route("/home")
def home():
#     if 'user' in Session:
    current_project = request.cookies.get('project')
    if 'user' in session:
        return render_template('home.html', title='Home', current_user=session['user'], current_project=current_project)
    else:
        return render_template('home.html', title='Home', current_user=dummyUser, current_project=current_project)
#     else:
#         return render_template('home.html', title='Home', current_user=User("", False, False))


# Router to sorting page
@app.route("/sorter")
def sorter():
    if 'user' not in session:
        return redirect(url_for('home'))
    docPair = dbhandler.getPair(request.cookies.get('project'))
    if type(docPair) == type(""):
        return render_template('nopairs.html', title='Check later', message=docPair, current_user=session['user'])
    file_one = docPair.getFirstContents().decode("utf-8")
    file_two = docPair.getSecondContents().decode("utf-8")
    return render_template('sorter.html', title='Sorter', file_one=file_one,
                            file_two=file_two, file_one_name=docPair.getFirst(),
                            file_two_name=docPair.getSecond(),
                            current_user=session['user'])

# Router to demo page
@app.route("/demo")
def demo():
    pass

# Router to about page
@app.route("/about", methods=['GET'])
def about():
    if 'user' in session:
        return render_template('about.html', current_user=session['user'])
    else:
        return render_template('about.html', current_user=dummyUser)

# Router to admin page
@app.route("/myadmin", methods=['GET', 'POST'])
def myadmin():
    # if 'user' not in session or not session['user'].get_is_admin():
    # return redirect(url_for('home'))
    # allFiles = [i for i in listdir(app.config['APP_DOCS'])]
    allFiles = []
    return render_template('myadmin.html', title='Admin',
                            allFiles=allFiles, current_user=session['user'])

# Router for sorted page
@app.route("/sorted")
def sorted():
    if 'user' not in session:
        return redirect(url_for('home'))
    if dbhandler.getNumberOfDocs(request.cookies.get('project')) == 0:
        return render_template('nopairs.html', title='Check later', message='No docs in this project', current_user=session['user'])
    sortedFiles, confidence, *args = dbhandler.getSorted(request.cookies.get('project'))
    confidence = confidence * 100
    confidence = round(confidence, 2)
    number_of_judgments = dbhandler.getNumberOfJudgments(request.cookies.get('project'))
    number_of_docs = dbhandler.getNumberOfDocs(request.cookies.get('project'))
    possible_judgments = number_of_docs * (number_of_docs - 1) * .5
    if type(sortedFiles) == type(""):
        success = False
    else:
        success= True
    return render_template('sorted.html', title='Sorted',
                            sortedFiles=sortedFiles,
                            current_user=session['user'],
                            confidence=confidence,
                            number_of_judgments=number_of_judgments,
                            number_of_docs=number_of_docs,
                            possible_judgments=possible_judgments,
                            success=success)

# Delete file route
@app.route("/deleteFile", methods=['POST'])
@login_required
def deleteFile():
    print("in deleteFile route with", request.form.get('id'))
    os.remove((app.config['APP_DOCS'] + '/' + request.form.get('id')))
    dbhandler.deleteFile(request.form.get('id'), request.cookies.get('project'))
    return redirect(url_for('myadmin'))

@app.route("/detectFiles", methods=['POST'])
@login_required
def detectFiles():
    print("in detectFiles route")
    dbhandler.detectFiles(request.cookies.get('project'))
    return redirect(url_for('myadmin'))

@app.route("/submitAnswer", methods=['POST'])
@login_required
def submitanswer():
    print("in submitAnswer route")
    print(request.form.get("harder"))
    harder = request.form.get("harder")
    easier = "";
    if harder == request.form.get("file_one_name"):
        easier = request.form.get("file_two_name")
    else:
        easier = request.form.get("file_one_name")
    judge = current_user=session['user']
    dbhandler.createJudgment(harder, easier, request.cookies.get('project'), judge)
    if isinstance(request.form.get('another_pair_checkbox'), type(None)):
        flash('Judgment submitted', 'success')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('sorter'))


ALLOWED_EXTENSIONS = {'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['POST'])
@login_required
def uploadFile():
    if request.method == 'POST':
        validFiles = []
        if 'file' not in request.files:
            return redirect(request.url)
        files = request.files.getlist("file")
        for file in files:
            if file.filename == '':
                print("No file selected for uploading")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                validFiles.append(file)
            else:
                flash('Allowed file types are txt', 'danger')
        flash(f'{len(validFiles)} file(s) successfully uploaded', 'success')
        dbhandler.addDocs(validFiles, request.cookies.get('project'))
        filenames = [x.filename for x in files]
        pairselector.create_acj(filenames, 10)
        return redirect(url_for('myadmin'))


@app.route("/addproject", methods=['POST'])
@login_required
def add_project():
    message = dbhandler.createProject(request.form.get('project_name'))
    print(message)
    return redirect(url_for('projectsdashboard'))
