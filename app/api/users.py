import json
import hashlib
import datetime

from app.api import bp
from app.api.errors import bad_request
from app.models import db, User
from flask import request, jsonify


@bp.route('/users/register', methods=['POST'])
def register():
    pass


@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json() or {}
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
                token_word = f'{user.login}{user.email}{user.surname}{datetime.datetime.now().timestamp()}'
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
