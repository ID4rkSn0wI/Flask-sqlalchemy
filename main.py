import datetime as dt

from flask import Flask, render_template, redirect, abort, request
from wtforms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.category import Category
from data.forms import LoginForm, RegisterForm, JobsForm, DepartmentsForm
from data.jobs import Jobs
from data.users import User
from data.departments import Department


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
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
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"
    user.department_id = 1
    db_sess.add(user)
    user2 = User()
    user2.surname = "Sissy"
    user2.name = "Miller"
    user2.age = 43
    user2.position = "colonist"
    user2.speciality = "pilot"
    user2.address = "module_1"
    user2.email = "sissy_miller@mars.org"
    user2.department_id = 1
    db_sess.add(user2)
    user3 = User()
    user3.surname = "Scott"
    user3.name = "Walter"
    user3.age = 66
    user3.position = "captain"
    user3.speciality = "ecologist"
    user3.address = "module_2"
    user3.email = "scott_walter@mars.org"
    user3.department_id = 2
    db_sess.add(user3)
    user4 = User()
    user4.surname = "Breaking"
    user4.name = "Bad"
    user4.age = 33
    user4.position = "colonist"
    user4.speciality = "meteorologist"
    user4.address = "module_2"
    user4.email = "breaking_bad@mars.org"
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


@app.route('/add_job',  methods=['GET', 'POST'])
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
    print(idd)
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == idd, (Jobs.team_leader == current_user) | (current_user.position == "captain")).first()
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
        job = db_sess.query(Jobs).filter(Jobs.id == idd, (Jobs.team_leader == current_user) | (current_user.position == "captain")).first()
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
            print(cats)
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
    jobs = db_sess.query(Jobs).filter(Jobs.id == idd, (Jobs.team_leader == current_user) | (current_user.position == "captain")).first()
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


@app.route('/add_department',  methods=['GET', 'POST'])
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


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=5000, host='127.0.0.1')
