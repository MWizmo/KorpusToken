from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


"""
Переделать логику регистрации, из User убрать role, team 
и настроить занесение этих данных в бд teams/membership
Разобраться с username
"""


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    login = db.Column(db.String(64), unique=True)
    tg_nickname = db.Column(db.String(64))
    tg_id = db.Column(db.String(64), unique=True)
    courses = db.Column(db.String(256))
    birthday = db.Column(db.String(32))
    education = db.Column(db.String(64))
    work_exp = db.Column(db.String(64))
    sex = db.Column(db.String(16))

    def __init__(self, email, login, tg_nickname,
                 courses, birthday, education, work_exp, sex, name, surname):
        self.name = name
        self.surname = surname
        self.email = email
        self.login = login
        self.tg_nickname = tg_nickname
        self.courses = courses
        self.birthday = birthday
        self.education = education
        self.work_exp = work_exp
        self.sex = sex

    def __repr__(self):
        return '<User: {}>'.format(self.login)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    text = db.Column(db.Text)


class QuestionsTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)


class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    type = db.Column(db.Integer)


class QuestionnaireInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questionnaire_id = db.Column(db.Integer)
    question_id = db.Column(db.Integer)
    question_num = db.Column(db.Integer)
    question_answ = db.Column(db.Text)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
