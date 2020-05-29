# -*- coding: utf-8 -*-
import datetime

# import jdcal
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    @staticmethod
    def check_cadet(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 3:
                return True
        return False

    @staticmethod
    def check_admin(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 1:
                return True
        return False

    @staticmethod
    def check_teamlead(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 4:
                return True
        return False

    @staticmethod
    def check_can_be_marked(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 3:
                teams = Membership.query.filter_by(user_id=current_user_id).all()
                for t in teams:
                    team = Teams.query.filter_by(id=t.team_id).first()
                    if team.type and team.type == 1:
                        return True
                #return True
        return False

    @staticmethod
    def check_chieftain(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 2:
                return True
        return False

    @staticmethod
    def check_tracker(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 5:
                return True
        return False

    @staticmethod
    def check_expert(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 6:
                return True
        return False

    @staticmethod
    def check_top_cadet(current_user_id):
        statuses = UserStatuses.query.filter_by(user_id=current_user_id).all()
        for status in statuses:
            if status.status_id == 7:
                return True
        return False

    @staticmethod
    def dict_of_responsibilities(current_user_id):
        return dict(admin=User.check_admin(current_user_id), cadet=User.check_cadet(current_user_id),
                    chieftain=User.check_chieftain(current_user_id), teamlead=User.check_teamlead(current_user_id),
                    can_be_marked=User.check_can_be_marked(current_user_id),
                    tracker=User.check_tracker(current_user_id), expert=User.check_tracker(current_user_id),
                    top_cadet=User.check_top_cadet(current_user_id))

    @staticmethod
    def get_full_name(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user.name[0] + '. ' + user.surname

    def __init__(self, email, login, tg_nickname,
                 courses, birthday, education,
                 work_exp, sex, name, surname,
                 token=None):
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
        self.token = token

    def __repr__(self):
        return '<User: {}>'.format(self.login)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):  # , include: dict
        data = {
            'id': self.id,
            'name': self.name,
            'surname': self.surname,
            'tg_nickname': self.tg_nickname,
            'tg_id': self.tg_id,
            'photo': self.photo,
            'sex': self.sex,
            'login': self.login,
            'email': self.email,
            'birthday': self.birthday,
            'education': self.education,
            'work_exp': self.work_exp,
            'membership': True if Membership.query.filter_by(user_id=self.id).first() else False
        }
        return data

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
    education = db.Column(db.String(128))
    work_exp = db.Column(db.String(256))
    sex = db.Column(db.String(16))
    chat_id = db.Column(db.String(64))
    state = db.Column(db.Integer)
    photo = db.Column(db.String(512))
    vk_url = db.Column(db.String(256))
    fb_url = db.Column(db.String(256))
    inst_url = db.Column(db.String(256))
    token = db.Column(db.String(64))


class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    type = db.Column(db.Integer)


class TeamRoles(db.Model):
    @staticmethod
    def check_team_lead(current_user_id, team_id=None):
        if team_id:
            if 1 in [user_role.role_id
                     for user_role in TeamRoles.query.filter_by(user_id=current_user_id, team_id=team_id).all()]:
                return True
            else:
                return False
        else:
            if 1 in [user_role.role_id for user_role in TeamRoles.query.filter_by(user_id=current_user_id).all()]:
                return True
            else:
                return False

    @staticmethod
    def dict_of_user_roles(current_user_id):
        return {'teamlead': {'exist': TeamRoles.check_team_lead(current_user_id),
                             'team_ids': [team.id for team in Membership.query.filter_by(user_id=current_user_id) if
                                          TeamRoles.check_team_lead(current_user_id, team.id)]}
                }

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))


class Membership(db.Model):
    @staticmethod
    def get_crew_of_team(team_id):
        team_users = db.session.query(User.id, User.name, User.surname) \
            .outerjoin(Membership, User.id == Membership.user_id) \
            .filter(Membership.team_id == team_id).all()

        return team_users

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


class QuestionnaireTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32))

    @staticmethod
    def is_opened():
        return len(QuestionnaireTable.query.filter_by(status='Active').all()) > 0

    @staticmethod
    def is_in_assessment():
        return len(QuestionnaireTable.query.filter_by(status='Ready for assessment').all()) > 0

    @staticmethod
    def current_questionnaire_id():
        q = QuestionnaireTable.query.filter_by(status='Active').first()
        if q is not None:
            return q.id
        else:
            return QuestionnaireTable.query.filter_by(status='Ready for assessment').first().id


class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    type = db.Column(db.Integer)
    questionnaire_id = db.Column(db.Integer)
    assessment = db.Column(db.Integer)


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
    # TODO: Допилить функцию и связать c questionnaire_info
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


class Axis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    is_opened = db.Column(db.Integer)

    @staticmethod
    def is_available(axis_id):
        return Axis.query.filter_by(id=axis_id).first().is_opened


class Criterion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    axis_id = db.Column(db.Integer)


class Voting(db.Model):
    @staticmethod
    def check_on_assessment(current_user_id, team_id, axis_id):
        if axis_id == 3:
            last_voting = Voting.query.filter_by(
                user_id=current_user_id, team_id=0, axis_id=axis_id
            ).all()
            if last_voting:
                last_voting = last_voting[-1].voting_id
            else:
                return True
        else:
            last_voting = Voting.query.filter_by(user_id=current_user_id, team_id=team_id, axis_id=axis_id).all()
            if last_voting:
                last_voting = last_voting[-1].voting_id
            else:
                return True
        if last_voting:
            if last_voting == VotingTable.current_voting_id():
                return False
            else:
                return True
        else:
            return True

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    axis_id = db.Column(db.Integer)
    voting_id= db.Column(db.Integer)


class VotingInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voting_id = db.Column(db.Integer)
    cadet_id = db.Column(db.Integer)
    criterion_id = db.Column(db.Integer)
    mark = db.Column(db.Integer)


class VotingTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(16))
    month = db.Column(db.String(32))

    @staticmethod
    def is_opened():
        return len(VotingTable.query.filter_by(status='Active').all()) > 0

    @staticmethod
    def current_voting_id():
        return VotingTable.query.filter_by(status='Active').first().id


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(256))
    date = db.Column(db.String(32))


class TopCadetsScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    score = db.Column(db.Integer)


class TopCadetsVoting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.Integer)
    date = db.Column(db.Date)


class WeeklyVoting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    date = db.Column(db.Date)
    criterion_id = db.Column(db.Integer)
    mark = db.Column(db.Integer)
    finished = db.Column(db.Integer)
