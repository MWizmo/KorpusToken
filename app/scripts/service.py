from app.models import User, QuestionnaireTable, VotingTable, Membership, TeamRoles


def get_access(current_user):
    return {'responsibilities': User.dict_of_responsibilities(current_user.id),
            'questionnaire_opened': QuestionnaireTable.is_opened(),
            'assessment_opened': VotingTable.is_opened(),
            'user_roles': TeamRoles.dict_of_user_roles(current_user.id),
            'team': Membership.team_participation(current_user.id)}


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
