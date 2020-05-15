import json
import hashlib
import datetime

from app.scripts.service import get_access
from app.api import bp
from app.api.errors import bad_request
from app.models import db, Questionnaire, Questions, QuestionnaireTable, Membership, QuestionnaireInfo, User
from flask import request, jsonify


@bp.route('/questionnaire/questionnaire_self', methods=['GET', 'POST'])
def questionnaire_self():
    if request.method == 'GET':
        payload = {
            'message': 'OK',
            'questions': [question.text for question in Questions.query.filter_by(type=1).all()[:4]]
        }

        response = jsonify(payload)
        response.status_code = 200
        return response
    else:
        data = request.get_json() or {}
        if type(data) == str:
            data = json.loads(data)
        if 'token' not in data:
            return bad_request('Must contain token')
        if 'answers' not in data:
            return bad_request('Must contain answers')
        print(data)
        payload = {}

        user = User.query.filter_by(token=data['token']).first()
        membership = Membership.query.filter_by(user_id=user.id).first()
        cur_quest = QuestionnaireTable.current_questionnaire_id()
        user_quest = Questionnaire.query.filter_by(user_id=user.id, type=1).all()
        if user_quest:
            user_quest = user_quest[-1]
        else:
            user_quest = -1

        if user_quest != -1:
            if cur_quest == user_quest.questionnaire_id:
                return bad_request('Already got')

        if user:
            user_access = get_access(user)
            print(user_access['responsibilities']['can_be_marked'], user_access['questionnaire_opened'])
            if user_access['responsibilities']['can_be_marked'] and user_access['questionnaire_opened']:
                if membership:
                    questionnaire = Questionnaire(
                        user_id=user.id,
                        team_id=membership.team_id,
                        date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                           datetime.datetime.now().day),
                        type=1, questionnaire_id=cur_quest, assessment=1
                    )
                else:
                    questionnaire = Questionnaire(
                        user_id=user.id,
                        date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                           datetime.datetime.now().day),
                        type=1, questionnaire_id=cur_quest, assessment=1
                    )
                db.session.add(questionnaire)
                db.session.commit()

                for i, question in enumerate(data['answers']):
                    question_obj = Questions.query.filter_by(text=question).first()
                    if question_obj:
                        answer = QuestionnaireInfo(
                            question_id=question_obj.id,
                            questionnaire_id=Questionnaire.query.all()[-1].id,
                            question_num=i+1,
                            question_answ=data['answers'][question]
                        )
                        db.session.add(answer)
                    else:
                        return bad_request(f'Question {i+1} doesnt appears')
                db.session.commit()

                payload['message'] = 'OK'
                response = jsonify(payload)
                response.status_code = 200
                print(payload)
                return response
            else:
                return bad_request('Cant be marked')
        else:
            return bad_request('Token invalid')


