from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 8961a30ff996

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    login = db.Column(db.String(64))
    tg_nickname = db.Column(db.String(64))
    team = db.Column(db.String(64))
    role = db.Column(db.String(64))
    courses = db.Column(db.String(256))
    birthday = db.Column(db.String(32))
    education = db.Column(db.String(64))
    work_exp = db.Column(db.String(64))
    sex = db.Column(db.String(16))

    def __init__(self, email, login, tg_nickname, team, role,
                 courses, birthday, education, work_exp, sex, username):
        #  self.id = id
        #  self.username = username
        self.email = email
        self.login = login
        self.tg_nickname = tg_nickname
        self.team = team
        self.role = role
        self.courses = courses
        self.birthday = birthday
        self.education = education
        self.work_exp = work_exp
        self.sex = sex
        self.username = username

    def __repr__(self):
        return f'<User: {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
