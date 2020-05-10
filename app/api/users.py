import json
import hashlib
import datetime

from app.api import bp
from app.api.errors import bad_request
from app.models import db, User, Teams, Membership, UserStatuses
from app.scripts.service import login_validating, email_validating
from flask import request, jsonify


@bp.route('/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        payload = {
            'teams': [team.name for team in Teams.query.all()]
        }
        response = jsonify(payload)
        response.status_code = 200
        return response
    elif request.method == 'POST':
        data = request.get_json() or {}
        if type(data) == str:
            data = json.loads(data)
        payload = {
            'message': '',
            'validation_errors': []
        }
        if len(data) >= 10:
            if not login_validating(data['login']):
                payload['message'] += 'Login validating failed. Login is already using. '
                payload['validation_errors'].append('login')
            if not email_validating(data['email']):
                payload['message'] += 'Email validating failed. Email is already using.'
                payload['validation_errors'].append('email')
            if len(payload['validation_errors']) > 0:
                response = jsonify(payload)
                response.status_code = 400
                return response

            data['birthday'] = datetime.datetime.strptime(data['birthday'], '%d-%m-%Y')
            token_word = '{}{}{}{}'.format(data["login"], data["email"], data["surname"],
                                           datetime.datetime.now().timestamp())                                  
            token_word = hashlib.sha256(token_word.encode()).hexdigest()
            user = User(
                data['email'],
                data['login'],
                data['tg_nickname'],
                data['courses'],
                data['birthday'],
                data['education'],
                data['work_exp'],
                data['sex'],
                data['name'],
                data['surname'],
                token_word
            )
            db.session.add(user)
            db.session.commit()

            user = User.query.filter_by(email=data['email']).first()
            if 'team' in data:
                user_team = Membership(user_id=user.id,
                                       team_id=Teams.query.filter_by(name=data['team']).first().id,
                                       role_id=0)
                db.session.add(user_team)
            user_status = UserStatuses(user_id=user.id, status_id=3)
            db.session.add(user_status)
            db.session.commit()

            payload['message'] = 'Registered'
            payload['token'] = token_word
            response = jsonify(payload)
            response.status_code = 200
            return response
        else:
            return bad_request('Got not enough DATA')


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if type(data) == str:
        data = json.loads(data)
    if ('login' not in data) or ('password' not in data):
        return bad_request('Must include login and password fields')

    user_login = data['login']
    user_password = data['password']
    user = User.query.filter_by(login=user_login).first()
    payload = {}
    if user:
        if user.check_password(user_password):
            payload['message'] = 'Logged'
            if not user.token:
                token_word = '{}{}{}{}'.format(user.login, user.email, user.surname, datetime.datetime.now().timestamp())
                user.token = hashlib.sha256(token_word.encode()).hexdigest()
                db.session.commit()
            payload['token'] = user.token
        else:
            payload['message'] = 'Login or password incorrect'
    else:
        payload['message'] = 'Login or password incorrect'

    response = jsonify(payload)
    response.status_code = 200
    return response


@bp.route('/users/get_users', methods=['GET'])
def get_users():
    pass
