import datetime as dt

from flask import Blueprint, Flask, render_template, redirect, abort, request, make_response, jsonify
from wtforms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.category import Category
from data.forms import LoginForm, RegisterForm, JobsForm, DepartmentsForm
from data.jobs import Jobs
from data.users import User
from data.departments import Department
from yandex_api import get_coordinates, write_img
import flask_restful
from flask_restful import reqparse, Api, Resource
from requests import get, post, delete

app = Flask(__name__)
jobs_blueprint = Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)
users_blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


def fill_tables(db_sess):
    department = Department()
    department.title = "doctors"
    department.email = "www_kkk@gmail.com"
    department.chief = 2
    db_sess.add(department)
    department2 = Department()
    department2.title = "mailers"
    department2.email = "fff_kkk@gmail.com"
    department2.chief = 3
    db_sess.add(department2)

    user = User()
    user.surname = "Scott"
    user.name = "Ridley"
    user.age = 21
    user.city_from = 'Moscow'
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"
    user.department_id = 1
    user.set_password("1234")
    db_sess.add(user)
    user2 = User()
    user2.surname = "Sissy"
    user2.name = "Miller"
    user2.age = 43
    user2.city_from = 'Syktyvkar'
    user2.position = "colonist"
    user2.speciality = "pilot"
    user2.address = "module_1"
    user2.email = "sissy_miller@mars.org"
    user2.set_password("1234")
    user2.department_id = 1
    db_sess.add(user2)
    user3 = User()
    user3.surname = "Scott"
    user3.name = "Walter"
    user3.age = 66
    user3.city_from = 'Voronesh'
    user3.position = "captain"
    user3.speciality = "ecologist"
    user3.address = "module_2"
    user3.email = "scott_walter@mars.org"
    user3.set_password("1337")
    user3.department_id = 2
    db_sess.add(user3)
    user4 = User()
    user4.surname = "Breaking"
    user4.name = "Bad"
    user4.age = 33
    user4.city_from = 'Saint Petersburg'
    user4.position = "colonist"
    user4.speciality = "meteorologist"
    user4.address = "module_2"
    user4.email = "breaking_bad@mars.org"
    user4.set_password("1488")
    user4.department_id = 2
    db_sess.add(user4)

    category = Category()
    category.name = "medicine"
    db_sess.add(category)
    category2 = Category()
    category2.name = "mail"
    db_sess.add(category2)
    job = Jobs()
    job.team_leader_id = 1
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = "2, 3"
    job.start_date = dt.datetime.now()
    job.is_finished = False
    job.categories = [category, category2]
    db_sess.add(job)

    db_sess.commit()


def main():
    db_sess = db_session.create_session()
    fill_tables(db_sess)
    db_sess.close()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def work_logs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template('work_logs.html', title='Work log', jobs=jobs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            city_from=form.city_from.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.job = form.job.data
        job.team_leader_id = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление новости',
                           form=form)


@app.route('/jobs/<int:idd>', methods=['GET', 'POST'])
@login_required
def edit_jobs(idd):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == idd, (Jobs.team_leader == current_user) | (
                current_user.position == "captain")).first()
        if job:
            form.job.data = job.job
            form.team_leader_id.data = job.team_leader_id
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            categories = job.categories
            ids = []
            for cat in categories:
                ids.append(str(cat.id))
            form.category.data = ', '.join(ids)
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == idd, (Jobs.team_leader == current_user) | (
                current_user.position == "captain")).first()
        if job:
            job.job = form.job.data
            job.team_leader_id = form.team_leader_id.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            categories = form.category.data
            cats = []
            for idd in categories.split(', '):
                category = db_sess.query(Category).filter(Category.id == idd).first()
                cats.append(category)
            job.categories = cats
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/jobs_delete/<int:idd>', methods=['GET', 'POST'])
@login_required
def jobs_delete(idd):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == idd,
                                      (Jobs.team_leader == current_user) | (current_user.position == "captain")).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/departments')
def departments():
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).all()
    return render_template('department_logs.html', title='', departments=departments)


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_departments():
    form = DepartmentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department()
        department.title = form.title.data
        department.chief = form.chief.data
        members_ds = form.members.data.split(', ')
        members_ids = []
        for idd in members_ds:
            members_ids.append(int(idd))
        members = []
        for member in db_sess.query(User).get(User.id.in_(members_ids)):
            members.append(member)
        department.members = members
        department.email = form.email.data
        db_sess.add(department)
        db_sess.commit()
        return redirect('/')
    return render_template('departments.html', title='Добавление новости',
                           form=form)


@app.route('/departments/<int:idd>', methods=['GET', 'POST'])
@login_required
def edit_departments(idd):
    form = DepartmentsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == idd,
                                                      Department.chief == current_user.id
                                                      ).first()
        if department:
            form.title.data = department.title
            form.chief.data = department.chief
            form.email.data = department.email
            members_ids = []
            for member in department.members:
                members_ids.append(str(member.id))
            form.members.data = ', '.join(members_ids)
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = db_sess.query(Department).filter(Department.id == idd,
                                                      Department.chief == current_user.id
                                                      ).first()
        if department:
            department.title = form.title.data
            department.chief = form.chief.data
            members_ds = form.members.data.split(', ')
            members_ids = []
            for idd in members_ds:
                members_ids.append(int(idd))
            members = []
            for member in db_sess.query(User).filter(User.id.in_(members_ids)):
                members.append(member)
            department.members = members
            department.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('departments.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/departments_delete/<int:idd>', methods=['GET', 'POST'])
@login_required
def department_delete(idd):
    db_sess = db_session.create_session()
    department = db_sess.query(Department).filter(Department.id == idd, Department.chief == current_user.id).first()
    if department:
        db_sess.delete(department)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@jobs_blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('job', 'work_size', "collaborators", 'team_leader.name'))
                 for item in jobs]
        }
    )


@jobs_blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        job.to_dict(only=('job', 'work_size', "collaborators", 'team_leader.name'))
    )


@jobs_blueprint.route('/api/jobs/<job_id>', methods=['GET'])
def get_job_by_id_error(job_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@jobs_blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not (all(key in request.json and isinstance(request.json[key], str) for key in ['job', 'collaborators']) and
              all(key in request.json and isinstance(request.json[key], int) for key in
                  ['team_leader_id', 'work_size']) and
              ("is_finished" in request.json and isinstance(request.json["is_finished"], bool))):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    job = Jobs(
        team_leader_id=request.json['team_leader_id'],
        job=request.json['job'],
        work_size=request.json['work_size'],
        collaborators=request.json['collaborators'],
        is_finished=request.json['is_finished']
    )
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'id': job.id})


@jobs_blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_jobs(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@jobs_blueprint.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_jobs_error(job_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@jobs_blueprint.route('/api/jobs/<int:job_id>', methods=['POST'])
def edit_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return make_response(jsonify({'error': 'Not found'}), 404)
    elif not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all((key in ['job', 'collaborators'] and isinstance(request.json[key], str)) or
                 (key in ['work_size', 'team_leader_id'] and isinstance(request.json[key], int)) or
                 (key == "is_finished" and isinstance(request.json[key], bool)) for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    if "team_leader_id" in request.json:
        job.team_leader_id = request.json["team_leader_id"]
    elif "job" in request.json:
        job.job = request.json["job"]
    elif "work_size" in request.json:
        job.work_size = request.json["work_size"]
    elif "collaborators" in request.json:
        job.collaborators = request.json["collaborators"]
    elif "is_finished" in request.json:
        job.is_finished = request.json["is_finished"]
    db_sess.commit()
    return jsonify({'success': 'OK'})


@jobs_blueprint.route('/api/jobs/<job_id>', methods=['POST'])
def edit_jobs_exc(job_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@users_blueprint.route('/api/users', methods=['GET'])
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(
                    only=('name', 'surname', "age", 'position', 'speciality', 'address', "department.title"))
                    for item in users]
        }
    )


@users_blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        user.to_dict(only=('name', 'surname', "age", 'position', 'speciality', 'address', 'department.title'))
    )


@users_blueprint.route('/api/users/<user_id>', methods=['GET'])
def get_user_by_id_error(user_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@users_blueprint.route('/api/users', methods=['POST'])
def create_users():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not (all(key in request.json and isinstance(request.json[key], str) for key in
                  ['name', 'surname', 'city_from', 'position', 'speciality', 'address', "email"]) and
              all(key in request.json and isinstance(request.json[key], int) for key in ['age', 'department_id']) and
              "hashed_password" in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    user = User(
        name=request.json['name'],
        surname=request.json['surname'],
        age=request.json['age'],
        city_from=request.json['city_from'],
        position=request.json['position'],
        speciality=request.json['speciality'],
        address=request.json['address'],
        department_id=request.json['department_id']
    )
    user.set_password(request.json['hashed_password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'id': user.id})


@users_blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_users(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@users_blueprint.route('/api/users/<user_id>', methods=['DELETE'])
def delete_users_error(user_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@users_blueprint.route('/api/users/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    elif not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all((key in ['name', 'surname', 'city_from', 'position', 'speciality', 'address', "email"] and
                  isinstance(request.json[key], str)) or (key in ['age', 'department_id'] and isinstance(request.json[key], int)) or
                 (key == 'hashed_password' and user.check_password(request.json['hashed_password'])) for key in request.json):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    if "name" in request.json:
        user.name = request.json["name"]
    elif "surname" in request.json:
        user.surname = request.json["surname"]
    elif "age" in request.json:
        user.age = request.json["age"]
    elif "city_from" in request.json:
        user.city_from = request.json["city_from"]
    elif "position" in request.json:
        user.position = request.json["position"]
    elif "speciality" in request.json:
        user.speciality = request.json["speciality"]
    elif "address" in request.json:
        user.address = request.json["address"]
    elif "email" in request.json:
        user.email = request.json["email"]
    elif "hashed_password" in request.json:
        user.set_password(request.json["hashed_password"])
    elif "department_id" in request.json:
        user.department_id = request.json["department_id"]
    db_sess.commit()
    return jsonify({'success': 'OK'})


@users_blueprint.route('/api/users/<user_id>', methods=['POST'])
def edit_users_exc(user_id):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/users_show/<int:user_id>', methods=['GET', "POST"])
def show_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    create_image(user_id, user.city_from)
    return render_template('show_user.html', title='Hometown', name=user.name, surname=user.surname,
                           city=user.city_from, img=f"{user_id}.png")


def create_image(idd, city):
    coords = get_coordinates(city)
    if coords:
        write_img(idd, coords)


def abort_if_users_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        flask_restful.abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify(users.to_dict(
            only=(
                'name', 'surname', "age", 'city_from', 'position', 'speciality', 'address', 'department_id')))

    def delete(self, user_id):
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        session.delete(users)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('surname', required=True, type=str)
parser.add_argument('age', required=True, type=int)
parser.add_argument('city_from', required=True, type=str)
parser.add_argument('position', required=True, type=str)
parser.add_argument('speciality', required=True, type=str)
parser.add_argument('address', required=True, type=str)
parser.add_argument('email', required=True, type=str)
parser.add_argument('department_id', required=True, type=int)
parser.add_argument('hashed_password', required=True)


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', "age", 'city_from', 'position', 'speciality', 'address', 'department_id'))
            for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            city_from=args['city_from'],
            position=args['position'],
            speciality=args['speciality'],
            address=args['address'],
            email=args['email'],
            department_id=args['department_id']
        )
        user.set_password(request.json['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})


def abort_if_jobs_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        flask_restful.abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_jobs_not_found(job_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(job_id)
        return jsonify(jobs.to_dict(
            only=('team_leader_id', 'job', "work_size", 'collaborators', 'is_finished')))

    def delete(self, job_id):
        abort_if_jobs_not_found(job_id)
        session = db_session.create_session()
        jobs = session.query(Jobs).get(job_id)
        session.delete(jobs)
        session.commit()
        return jsonify({'success': 'OK'})


job_parser = reqparse.RequestParser()
job_parser.add_argument('team_leader_id', required=True, type=int)
job_parser.add_argument('job', required=True, type=str)
job_parser.add_argument('work_size', required=True, type=int)
job_parser.add_argument('collaborators', required=True, type=str)
job_parser.add_argument('is_finished', required=True, type=bool)


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('team_leader_id', 'job', "work_size", 'collaborators', 'is_finished')) for item in jobs]})

    def post(self):
        args = job_parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader_id=args['team_leader_id'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=args['is_finished']
        )
        session.add(job)
        session.commit()
        return jsonify({'id': job.id})


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_blueprint)
    app.register_blueprint(users_blueprint)
    api.add_resource(UsersListResource, '/api/v2/users')
    api.add_resource(UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(JobsListResource, '/api/v2/jobs')
    api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')
    app.run()
