from app.models import User, QuestionnaireTable, VotingTable, Membership, TeamRoles, Questionnaire


def get_access(current_user):
    return {'responsibilities': User.dict_of_responsibilities(current_user.id),
            'questionnaire_opened': QuestionnaireTable.is_opened(),
            'assessment_opened': VotingTable.is_opened(),
            'user_roles': TeamRoles.dict_of_user_roles(current_user.id),
            'team': Membership.team_participation(current_user.id)}


def get_questionnaires_access(current_user):
    accesses = {}
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=1).all()
    if user_quest:
        user_quest = user_quest[-1]
    else:
        user_quest = -1

    if user_quest != -1:
        if cur_quest == user_quest.questionnaire_id:
            accesses['questionnaire_self'] = False
        else:
            accesses['questionnaire_self'] = True
    else:
        if User.check_cadet(current_user.id) or User.check_teamlead(current_user.id):
            accesses['questionnaire_self'] = True
        else:
            accesses['questionnaire_self'] = False

    user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=2).all()
    if user_quest:
        user_quest = user_quest[-1]
    else:
        user_quest = -1

    if user_quest != -1:
        if cur_quest == user_quest.questionnaire_id:
            accesses['questionnaire_team'] = False
        else:
            accesses['questionnaire_team'] = True
    else:
        accesses['questionnaire_team'] = True

    return accesses


def login_validating(login):
    user = User.query.filter_by(login=login).first()
    if user is not None:
        return False
    return True


def email_validating(email):
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return False
    return True
