from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    @staticmethod
    def check_cadet(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id)
        for status in statuses:
            if status.status_id == 3:
                return True
        return False

    @staticmethod
    def check_admin(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id)
        for status in statuses:
            if status.status_id == 1:
                return True
        return False

    @staticmethod
    def check_teamlead(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id)
        for status in statuses:
            if status.status_id == 4:
                return True
        return False

    @staticmethod
    def check_chieftain(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id)
        for status in statuses:
            if status.status_id == 2:
                return True
        return False

    @staticmethod
    def dict_of_responsibilities(current_user_id):
        return dict(admin=User.check_admin(current_user_id), cadet=User.check_cadet(current_user_id),
                    chieftain=User.check_chieftain(current_user_id), teamlead=User.check_teamlead(current_user_id))

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
    chat_id = db.Column(db.String(64))
    state = db.Column(db.Integer)
    photo = db.String(db.String(512))

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
    @staticmethod
    def get_crew_of_team(team_id):
        return db.session.query(User.id, User.name, User.surname) \
            .outerjoin(Membership, User.id == Membership.user_id) \
            .filter(Membership.team_id == team_id).all()

    @staticmethod
    def team_participation(current_user_id):
        if Membership.query.filter_by(user_id=current_user_id).first():
            return True
        return False

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


class Statuses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(64), unique=True)


class UserStatuses(db.Model):
    # Допилить функцию и связать c questionnaire_info
    @staticmethod
    def get_user_statuses(user_id):
        user_statuses = UserStatuses.query.filter_by(user_id=user_id)
        if len(user_statuses) > 1:
            statuses = []
            for user_status in user_statuses:
                statuses.append(user_status.status)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    status_id = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
