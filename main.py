import datetime

from flask import Flask, render_template, redirect
from wtforms.fields.numeric import IntegerField

from data import db_session
from data.jobs import Jobs
from data.users import User
from data.departments import Department
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def add_users(db_sess):
    user = User()
    user.surname = "Scott"
    user.name = "Ridley"
    user.age = 21
    user.position = "captain"
    user.speciality = "research engineer"
    user.address = "module_1"
    user.email = "scott_chief@mars.org"
    db_sess.add(user)
    user = User()
    user.surname = "Sissy"
    user.name = "Miller"
    user.age = 43
    user.position = "colonist"
    user.speciality = "pilot"
    user.address = "module_1"
    user.email = "sissy_miller@mars.org"
    db_sess.add(user)
    user = User()
    user.surname = "Scott"
    user.name = "Walter"
    user.age = 66
    user.position = "captain"
    user.speciality = "ecologist"
    user.address = "module_2"
    user.email = "scott_walter@mars.org"
    db_sess.add(user)
    user = User()
    user.surname = "Breaking"
    user.name = "Bad"
    user.age = 33
    user.position = "colonist"
    user.speciality = "meteorologist"
    user.address = "module_2"
    user.email = "breaking_bad@mars.org"
    db_sess.add(user)
    department = Department()
    department.email = "123"
    department.title = "roar"
    department.chief = 1
    department.members.append(user)
    db_sess.add(department)


def add_jobs(db_sess):
    job = Jobs()
    job.team_leader = 1
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = '2, 3'
    job.start_date = datetime.datetime.now()
    job.is_finished = False
    db_sess.add(job)


def fill_tables(db_sess):
    add_users(db_sess)
    add_jobs(db_sess)

    db_sess.commit()


def main():
    db_sess = db_session.create_session()
    fill_tables(db_sess)
    db_sess.close()


@app.route('/')
def work_logs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    for job in jobs:
        team_leader = db_sess.query(User).filter(User.id == job.team_leader).first()
        job.team_leader = f"{team_leader.surname} {team_leader.name}"
    return render_template('work_logs.html', title='', jobs=jobs)


class RegisterForm(FlaskForm):
    email = EmailField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    db_sess = db_session.create_session()
    # main()
    print(db_sess.query(Department).all())
    # app.run(port=5000, host='127.0.0.1')
