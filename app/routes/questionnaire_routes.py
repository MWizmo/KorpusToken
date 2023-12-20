# -*- coding: utf-8 -*-
import datetime, os, csv, threading
from app import app, db
from app.scripts import graphs
from app.scripts.service import get_access, log
from app.models import SkillKeyword, User, Questions, QuestionnaireInfo, Questionnaire, QuestionnaireTable, Membership, \
    UserStatuses, Statuses, Axis, Criterion, Voting, VotingInfo, TeamRoles, Log, TopCadetsScore, TopCadetsVoting, \
    VotingTable, WeeklyVoting, WeeklyVotingMembers, BudgetRecord, Transaction, EthExchangeRate, TokenExchangeRate, \
    Profit, KorpusServices, ServicePayments, Budget, Skill, WorkExperience, Language, QuestionnairePositionEnergy
from flask import render_template, redirect, url_for, request
from sqlalchemy import func
from app.forms import *
from flask_login import current_user, login_required


@app.route('/questionnaire_position', methods=['GET'])
@login_required
def questionnaire_position():
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    # user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=3).all()
    user_quest = QuestionnairePositionEnergy.query.filter(QuestionnairePositionEnergy.questionnaire_id == cur_quest,
                                                          QuestionnairePositionEnergy.cadet_id == current_user.id,
                                                          QuestionnairePositionEnergy.type == 3).all()
    if user_quest:
        return redirect('/questionnaire_energy')
        # user_quest = user_quest[-1]
        # if user_quest.questionnaire_id == cur_quest:
        #     if len(QuestionnaireInfo.query.filter_by(questionnaire_id=user_quest.id).all()) == 1:
        #         return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
        #     else:
        #         membership = Membership.query.filter_by(user_id=current_user.id).first()
        #         if not membership:
        #             return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
        #         else:
        #             return redirect('/questionnaire_energy')
    q = Questions.query.filter_by(type=3).first()
    membership = Membership.query.filter_by(user_id=current_user.id).all()
    teams_ids = []
    for m in membership:
        team = Teams.query.get(m.team_id)
        if team.type in [1]:
            teams_ids.append(team.id)
    users_ids = set()
    for t in teams_ids:
        m = Membership.query.filter(Membership.team_id == t, Membership.user_id != current_user.id).all()
        for u in m:
            users_ids.add(u.user_id)
    users = []
    for u in users_ids:
        user = User.query.get(u)
        users.append((user.id, user.name, user.surname))
    if len(users_ids):
        return render_template('questionnaire/questionnaire_position.html', title='Анкетирование - ясность позиции',
                           users=users, q=q)
    else:
        return redirect('/questionnaire_energy')


@app.route('/fix_quest_position', methods=['POST'])
@login_required
def fix_quest_position():
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    # quest = Questionnaire(user_id=current_user.id, team_id=int(request.form.get('team_id')), type=3,
    #                       questionnaire_id=cur_quest, assessment=1, date=datetime.datetime.now())
    # db.session.add(quest)
    # db.session.commit()
    for value in request.form:
        items = value.split('_')
        answer = QuestionnairePositionEnergy(questionnaire_id=cur_quest, type=3, cadet_id=int(items[1]),
                                             voted_id=int(items[2]), question_answ=int(request.form.get(value)))
        db.session.add(answer)
        db.session.commit()
    return redirect('/questionnaire_energy')


@app.route('/fix_quest_energy', methods=['POST'])
@login_required
def fix_quest_energy():
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    # quest = Questionnaire(user_id=current_user.id, team_id=int(request.form.get('team_id')), type=3,
    #                       questionnaire_id=cur_quest, assessment=1, date=datetime.datetime.now())
    # db.session.add(quest)
    # db.session.commit()
    for value in request.form:
        items = value.split('_')
        answer = QuestionnairePositionEnergy(questionnaire_id=cur_quest, type=4, cadet_id=int(items[1]),
                                             voted_id=int(items[2]), question_answ=int(request.form.get(value)))
        db.session.add(answer)
        db.session.commit()
    return redirect('/questionnaire_self')


@app.route('/questionnaire_energy', methods=['GET'])
@login_required
def questionnaire_energy():
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    # user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=3).all()
    user_quest = QuestionnairePositionEnergy.query.filter(QuestionnairePositionEnergy.questionnaire_id == cur_quest,
                                                          QuestionnairePositionEnergy.cadet_id == current_user.id,
                                                          QuestionnairePositionEnergy.type == 4).all()
    if user_quest:
        return redirect('/questionnaire_self')
        # user_quest = user_quest[-1]
        # if user_quest.questionnaire_id == cur_quest:
        #     if len(QuestionnaireInfo.query.filter_by(questionnaire_id=user_quest.id).all()) == 1:
        #         return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
        #     else:
        #         membership = Membership.query.filter_by(user_id=current_user.id).first()
        #         if not membership:
        #             return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
        #         else:
        #             return redirect('/questionnaire_energy')
    q = Questions.query.filter_by(type=4).first()
    membership = Membership.query.filter_by(user_id=current_user.id).all()
    teams_ids = []
    for m in membership:
        team = Teams.query.get(m.team_id)
        if team.type in [1]:
            teams_ids.append(team.id)
    users_ids = set()
    for t in teams_ids:
        m = Membership.query.filter(Membership.team_id == t, Membership.user_id != current_user.id).all()
        for u in m:
            users_ids.add(u.user_id)
    users = []
    for u in users_ids:
        user = User.query.get(u)
        users.append((user.id, user.name, user.surname))
    if len(users_ids):
        return render_template('questionnaire/questionnaire_energy.html', title='Анкетирование - энергия', users=users, q=q)
    else:
        return redirect('/questionnaire_self')


@app.route('/questionnaire_self', methods=['GET', 'POST'])
@login_required
def questionnaire_self():
    log('Просмотр страницы с личной анкетой')
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=1).all()
    if user_quest:
        user_quest = user_quest[-1]
        if user_quest.questionnaire_id == cur_quest:
            if len(QuestionnaireInfo.query.filter_by(questionnaire_id=user_quest.id).all()) == 9:
                return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
            else:
                membership = Membership.query.filter_by(user_id=current_user.id).first()
                if not membership:
                    return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
                else:
                    return redirect('/questionnaire_team')

    form = QuestionnairePersonal()
    questions = Questions.query.filter_by(type=1)  # type=1 - вопросы 1-го типа, т. е. личные
    membership = Membership.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        if membership:
            q = Questionnaire(user_id=current_user.id,
                              team_id=membership.team_id,
                              date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                                 datetime.datetime.now().day),
                              type=1, questionnaire_id=cur_quest, assessment=1)
        else:
            q = Questionnaire(user_id=current_user.id,
                              date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                                 datetime.datetime.now().day),
                              type=1, questionnaire_id=cur_quest, assessment=1)
        db.session.add(q)
        db.session.commit()
        answs = [form.qst_personal_growth.data, form.qst_controllability.data,
                 form.qst_selfcontrol.data, form.qst_strategy.data]
        i = 0

        for question in questions[:4]:
            answ = QuestionnaireInfo(question_id=question.id,
                                     questionnaire_id=Questionnaire.query.all()[-1].id,
                                     question_num=i + 1,
                                     question_answ=answs[i])
            db.session.add(answ)
            i += 1
        db.session.commit()
        log('Заполнение личной анкеты')
        return redirect('/questionnaire_team')

    return render_template('questionnaire/questionnaire_self.html', title='Личная анкета', form=form, q1=questions[0].text,
                           q2=questions[1].text, q3=questions[2].text, q4=questions[3].text,
                           access=get_access(current_user), membership=membership)


@app.route('/questionnaire_team', methods=['GET', 'POST'])
@login_required
def questionnaire_team():
    log('Просмотр страницы с командной анкетой')
    membership = Membership.query.filter_by(user_id=current_user.id).first()
    if not membership:
        return redirect('/participate')
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    user_quest = Questionnaire.query.filter_by(user_id=current_user.id, type=2).all()
    if user_quest:
        teams = Membership.query.filter_by(user_id=current_user.id).all()
        teams_for_voting = [team.id for team in Teams.get_teams_for_voting()]
        teams_id = [Teams.query.filter(Teams.id == t.team_id, Teams.id.in_(teams_for_voting)).first() for t in teams]
        teams_id = [t for t in teams_id if t]
        if len(teams_id) == 1:
            user_quest = user_quest[-1]
            if user_quest.questionnaire_id == cur_quest and \
                    len(QuestionnaireInfo.query.filter_by(questionnaire_id=user_quest.id).all()) == 5:
                return render_template('questionnaire/questionnaire_error.html',
                                       access=get_access(current_user))
    teammates = []
    # lst_teammates_bd = Membership.query.filter_by(
    #     team_id=Membership.query.filter_by(user_id=current_user.id).first().team_id)
    teams = Membership.query.filter_by(user_id=current_user.id).all()
    teams_for_voting = [team.id for team in Teams.get_teams_for_voting()]
    teams_id = [Teams.query.filter(Teams.id == t.team_id, Teams.id.in_(teams_for_voting)).first() for t in teams]
    teams_id = [t.id for t in teams_id if t]
    if len(teams_id) == 1:
        team_id = teams_id[0]
    else:
        done_teams = [q.team_id for q in
                      Questionnaire.query.filter_by(user_id=current_user.id, type=2, questionnaire_id=cur_quest).all()]
        if len(teams_id) == len(done_teams):
            return render_template('questionnaire/questionnaire_error.html', access=get_access(current_user))
        else:
            team_id = list(set(teams_id).difference(set(done_teams)))[0]
    lst_teammates_bd = Membership.query.filter(Membership.team_id == team_id,
                                               Membership.user_id != current_user.id).all()
    for teammate in lst_teammates_bd:
        if teammate.user_id == current_user.id or not (User.check_cadet(teammate.user_id)):
            continue
        try:
            cur_user = User.query.filter_by(id=teammate.user_id).first()
            name = cur_user.name
            surname = cur_user.surname
            teammates.append({'id': teammate.user_id, 'name': '{} {}'.format(name, surname)})
        except Exception as e:
            pass
    if len(teammates) == 0:
        return redirect('/participate')
    form = QuestionnaireTeam()
    questions = Questions.query.filter_by(type=2)
    if form.validate_on_submit():
        q = Questionnaire(user_id=current_user.id, team_id=team_id,
                          date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                             datetime.datetime.now().day),
                          type=2, questionnaire_id=cur_quest, assessment=1)

        db.session.add(q)
        db.session.commit()

        answs = [form.qst_q1.data, form.qst_q2.data, form.qst_q3.data, form.qst_q4.data, form.qst_q5.data]
        i = 0

        for question in questions[:5]:
            answ = QuestionnaireInfo(question_id=question.id,
                                     questionnaire_id=Questionnaire.query.all()[-1].id,
                                     question_num=i + 1,
                                     question_answ=answs[i])
            db.session.add(answ)
            i += 1
        db.session.commit()
        log('Заполнение командной анкеты')
        done_teams = [q.team_id for q in
                      Questionnaire.query.filter_by(user_id=current_user.id, type=2, questionnaire_id=cur_quest).all()]
        if len(teams_id) == len(done_teams):
            return redirect('/participate')
        else:
            return redirect(url_for('questionnaire_team'))
    team_title = Teams.query.filter_by(id=team_id).first().name
    return render_template('questionnaire/questionnaire_team.html', title='Командная анкета', teammates=teammates, form=form,
                           q1=questions[0].text, q2=questions[1].text, q3=questions[2].text, q4=questions[3].text,
                           q5=questions[4].text, team_title=team_title,
                           access=get_access(current_user))


@app.route('/question_adding', methods=['POST', 'GET'])
@login_required
def question_adding():
    if not User.check_admin(current_user.id):
        log('Попытка просмотра страницы добавления вопросов (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    log('Просмотр страницы с редактированием вопросов')
    type_of_questionnaire = int(request.args.get('type')) if request.args.get('type') else None
    form = QuestionAdding()

    if type_of_questionnaire:
        log('Просмотр страницы с редактированием вопросов для анкеты {}-го типа'.format(type_of_questionnaire))
        q = Questions.query.filter_by(type=type_of_questionnaire).all()[:5]
        questions = [qst.text for qst in q]
        if form.validate_on_submit():
            new_questions = [(form.question_1.data, 0), (form.question_2.data, 1), (form.question_3.data, 2),
                             (form.question_4.data, 3), (form.question_5.data, 4)]
            new_questions = [question for question in new_questions if question[0].replace(' ', '')]
            for question in new_questions:
                q[question[1]].text = question[0]

            db.session.commit()
            log('Изменение вопроса(ов) {}-го типа c id {} '.format(type_of_questionnaire,
                                                                   [question_id[1] for question_id in new_questions]))
            return redirect(url_for('question_adding'))
        return render_template('questionnaire/question_adding.html', title='Конструктор вопросов', form=form, successful=False,
                               type=True,
                               questions=questions,
                               access=get_access(current_user))
    return render_template('questionnaire/question_adding.html', title='Конструктор вопросов', type=False,
                           access=get_access(current_user))


@app.route('/graphs_teams')
@login_required
def graphs_teams():
    if not User.check_admin(current_user.id):
        log('Попытка просмотра страницы с выбором команды для генерации графов (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    log('Просмотр страницы с выбором команды для генерации графов')
    return render_template('questionnaire/graphs_teams.html', title='Грязный багоюзер',
                           access=get_access(current_user),
                           teams=[(team.id, team.name) for team in Teams.get_teams_for_voting()])


def get_questionnaire_progress():
    questionnaire = dict(
        max_particip=0,
        already_self=0,
        already_team=0,
        all_team_particip=0,
        participaters=[],
        participaters_self_ids=[],
        participaters_team_ids=[],
        participated_self=[],
        participated_team=[],
    )
    cur_questionnaire = QuestionnaireTable.query.filter_by(status='Active').first().id
    if User.query.all():
        for user in User.query.all():
            if User.check_can_be_marked(user.id):
                questionnaire['participaters'].append(user.id)
                questionnaire['participaters_self_ids'].append(user.id)
                questionnaire['max_particip'] += 1
                if User.is_in_team(user.id):
                    questionnaire['all_team_particip'] += 1
                    questionnaire['participaters_team_ids'].append(user.id)
            if Questionnaire.query.filter_by(user_id=user.id, type=1, assessment=1,
                                             questionnaire_id=cur_questionnaire).first():
                # for qst in Questionnaire.query.filter_by(user_id=user.id, type=1):
                #     if qst.questionnaire_id == cur_questionnaire:
                questionnaire['already_self'] += 1
                questionnaire['participated_self'].append(user.id)
            if Questionnaire.query.filter_by(user_id=user.id, type=2, assessment=1,
                                             questionnaire_id=cur_questionnaire).first():
                # for qst in Questionnaire.query.filter_by(user_id=user.id, type=2):
                #     if qst.questionnaire_id == cur_questionnaire:
                questionnaire['already_team'] += 1
                questionnaire['participated_team'].append(user.id)
    not_participated_self_ids = [user for user in questionnaire['participaters_self_ids']
                                 if user not in questionnaire['participated_self']]
    not_participated_self_names = [User.query.filter_by(id=user).first().name
                                   for user in questionnaire['participaters_self_ids']
                                   if user not in questionnaire['participated_self']]
    not_participated_self_surnames = [User.query.filter_by(id=user).first().surname
                                      for user in questionnaire['participaters_self_ids']
                                      if user not in questionnaire['participated_self']]
    # not_participated_self_statuses = [Statuses.query.filter_by(
    #     id=UserStatuses.query.filter_by(
    #         user_id=user).first().status_id).first().status
    #                                   for user in questionnaire['participaters_self_ids']
    #                                   if user not in questionnaire['participated_self']]
    # not_participated_self_teams = [Teams.query.filter_by(
    #     id=Membership.query.filter_by(user_id=user).first().team_id
    # ).first().name
    #                                for user in questionnaire['participaters_self_ids']
    #                                if user not in questionnaire['participated_self']]
    not_participated_self_teams = []
    for user in questionnaire['participaters_self_ids']:
        if user not in questionnaire['participated_self']:
            teams = Membership.query.filter_by(user_id=user).all()
            teams_for_voting = [team.id for team in Teams.get_teams_for_voting()]
            teams_id = [Teams.query.filter(Teams.id == t.team_id, Teams.id.in_(teams_for_voting)).first() for t in
                        teams]
            teams_id = [t for t in teams_id if t]
            if len(teams_id) > 0:
                not_participated_self_teams.append(', '.join([team.name for team in teams_id]))
            else:
                not_participated_self_teams.append('-')
    not_participated_self_info = []

    for i in range(len(not_participated_self_ids)):
        not_participated_self_info.append([not_participated_self_ids[i], not_participated_self_names[i],
                                           not_participated_self_surnames[i], not_participated_self_teams[i]])

    not_participated_team_ids = [user for user in questionnaire['participaters_team_ids']
                                 if user not in questionnaire['participated_team']]
    not_participated_team_names = [User.query.filter_by(id=user).first().name
                                   for user in questionnaire['participaters_team_ids']
                                   if user not in questionnaire['participated_team']]
    not_participated_team_surnames = [User.query.filter_by(id=user).first().surname
                                      for user in questionnaire['participaters_team_ids']
                                      if user not in questionnaire['participated_team']]
    not_participated_team_teams = []
    for user in questionnaire['participaters_team_ids']:
        if user not in questionnaire['participated_team']:
            teams = Membership.query.filter_by(user_id=user).all()
            teams_for_voting = [team.id for team in Teams.get_teams_for_voting()]
            teams_id = [Teams.query.filter(Teams.id == t.team_id, Teams.id.in_(teams_for_voting)).first() for t in
                        teams]
            teams_id = [t for t in teams_id if t]
            if len(teams_id) > 0:
                not_participated_team_teams.append(', '.join([team.name for team in teams_id]))
            else:
                not_participated_team_teams.append('-')
    # not_participated_team_teams = [Teams.query.filter(
    #     Teams.id==Membership.query.filter_by(user_id=user).first().team_id, Teams.type==1
    # ).first().name
    #                                for user in questionnaire['participaters_team_ids']
    #                                if user not in questionnaire['participated_team']]

    not_participated_team_info = []

    for i in range(len(not_participated_team_ids)):
        not_participated_team_info.append([not_participated_team_ids[i], not_participated_team_names[i],
                                           not_participated_team_surnames[i], not_participated_team_teams[i]])
    counter = len(TopCadetsVoting.query.all())
    return counter, questionnaire, not_participated_team_info, not_participated_self_info


@app.route('/questionnaire_progress', methods=['POST', 'GET'])
@login_required
def questionnaire_progress():
    # if not User.check_admin(current_user.id):
    #     log('Попытка просмотра страницы с прогрессом анкетирования (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            access=get_access(current_user))
    log('Просмотр страницы с прогрессом анкетирования')
    d1 = datetime.date.today()
    d2 = datetime.date(d1.year - 1, d1.month, d1.day)
    delta = d1 - d2
    monthes = []
    month_dict = {'December': 'декабрь', 'January': 'январь', 'February': 'февраль', 'March': 'март', 'April': 'апрель',
                  'May': 'май',
                  'June': 'июнь', 'July': 'июль', 'August': 'август', 'September': 'сентябрь', 'October': 'октябрь',
                  'November': 'ноябрь'}
    for i in range(delta.days + 1):
        month = (d2 + datetime.timedelta(i)).strftime('%B')
        if month in month_dict:
            month = month_dict[month]
        row = f"{month} {(d2 + datetime.timedelta(i)).strftime('%Y')}г."
        if row not in monthes:
            monthes.append(row)
    monthes = monthes[::-1]

    form = StartAssessmentForm()
    if form.validate_on_submit():
        if QuestionnaireTable.is_opened():
            return render_template('questionnaire/questionnaire_progress.html', title='Прогресс голосования',
                                   access=get_access(current_user), form=form,
                                   msg='Сначала надо завершить текущий процесс анкетирования')
        assessment_status = VotingTable(status='Active', month_from=form.month1.data, month_to=form.month2.data)
        db.session.add(assessment_status)
        db.session.commit()
        log('Открыл оценку')
        return redirect('voting_progress')
    is_opened = QuestionnaireTable.is_opened()
    if is_opened:
        counter, questionnaire, not_participated_team_info, not_participated_self_info = get_questionnaire_progress()
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс анкетирования',
                               access=get_access(current_user), counter=counter,
                               questionnaire=questionnaire, not_participated_self=not_participated_self_info,
                               not_participated_team=not_participated_team_info)
    elif QuestionnaireTable.is_in_assessment():
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', ready=True,
                               access=get_access(current_user), form=form, monthes=monthes)
    elif VotingTable.current_fixed_voting_id():
        cur_id = VotingTable.current_fixed_voting_id()
        filename = 'results_' + str(cur_id) + '.csv'
        # if os.path.isfile(os.path.join(app.root_path + '/results', filename)):
        user_info = list()
        with open(os.path.join(app.root_path + '/results', filename)) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                user_marks = row[0].split(';')
                user_marks.append(sum(int(item) for item in row[0].split(';')[1:]))
                user_info.append(user_marks)
        user_info.sort(key=lambda i: i[-1], reverse=True)
        criterions = [c.name for c in Criterion.query.all()]
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', fixed_id=cur_id,
                               access=get_access(current_user), criterions=criterions, user_info=user_info)
    elif VotingTable.current_fixed2_voting_id():
        cur_id = VotingTable.current_fixed2_voting_id()
        filename = 'results_' + str(cur_id) + '.csv'
        # if os.path.isfile(os.path.join(app.root_path + '/results', filename)):
        user_info = list()
        with open(os.path.join(app.root_path + '/results', filename)) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                user_marks = row[0].split(';')
                user_marks.append(sum(int(item) for item in row[0].split(';')[1:]))
                user_info.append(user_marks)
        user_info.sort(key=lambda i: i[-1], reverse=True)
        criterions = [c.name for c in Criterion.query.all()]
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', fixed2_id=cur_id,
                               access=get_access(current_user), criterions=criterions, user_info=user_info)
    elif VotingTable.current_emission_voting_id():
        cur_id = VotingTable.current_emission_voting_id()
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', emission_id=cur_id,
                               access=get_access(current_user))
    elif VotingTable.current_distribution_voting_id():
        cur_id = VotingTable.current_distribution_voting_id()
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', emission_id=cur_id,
                               access=get_access(current_user))
    elif VotingTable.is_opened():
        cur_id = VotingTable.current_voting_id()
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки', active_id=cur_id,
                               access=get_access(current_user))
    else:
        return render_template('questionnaire/questionnaire_progress.html', title='Прогресс оценки',
                               access=get_access(current_user))


def make_all_graphs(team_id):
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    questionaires = Questionnaire.query.filter(Questionnaire.team_id == team_id, Questionnaire.type == 2,
                                               Questionnaire.questionnaire_id == cur_quest).all()
    res = list()
    for q in questionaires:
        user_res = [User.get_full_name(q.user_id)]
        user_answers = QuestionnaireInfo.query.filter_by(questionnaire_id=q.id).all()
        for answer in user_answers:
            user_res.append(User.get_full_name(int(answer.question_answ)))
        res.append(user_res)
    t = threading.Thread(target=graphs.Forms.command_form, args=([], res, team_id, cur_quest))
    t.setDaemon(True)
    t.start()
    t.join()


@app.route('/make_graphs')
@login_required
def make_graphs():
    if not User.check_admin(current_user.id):
        log('Попытка генерации графов (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))

    team_id = int(request.args.get('team_id'))
    cur_quest = QuestionnaireTable.current_questionnaire_id()
    questionaires = Questionnaire.query.filter(Questionnaire.team_id == team_id, Questionnaire.type == 2,
                                               Questionnaire.questionnaire_id == cur_quest).all()
    res = list()
    for q in questionaires:
        user_res = [User.get_full_name(q.user_id)]
        user_answers = QuestionnaireInfo.query.filter_by(questionnaire_id=q.id).all()
        for answer in user_answers:
            user_res.append(User.get_full_name(int(answer.question_answ)))
        res.append(user_res)

    t = threading.Thread(target=graphs.Forms.command_form, args=([], res, team_id, cur_quest))
    t.setDaemon(True)
    t.start()

    t.join()
    log('Генерация графов для команды с id {}'.format(team_id))
    return render_template('questionnaire/graphs_teams.html', title='Выбор команды для графов',
                           access=get_access(current_user),
                           teams=[(team.id, team.name) for team in Teams.get_teams_for_voting()],
                           message='Графы для команды успешно сформированы')


@app.route('/finish_questionnaire')
@login_required
def finish_questionnaire():
    if not User.check_admin(current_user.id):
        log('Попытка закрыть анкету (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    questionnaire = QuestionnaireTable.query.filter_by(status='Active').first()
    questionnaire.status = 'Ready for assessment'
    db.session.commit()
    teams = Teams.query.all()
    for t in teams:
        # requests.get(f'/f?team_id={t.id}')
        make_all_graphs(t.id)
    log('Закрытие анкетирования')
    return redirect('questionnaire_progress')


@app.route('/start_questionnaire')
@login_required
def start_questionnaire():
    if not User.check_admin(current_user.id):
        log('Попытка создать анкету (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    questionnaire = QuestionnaireTable(status='Active')
    db.session.add(questionnaire)
    db.session.commit()
    log('Открытие анкетирования')
    return redirect('questionnaire_progress')


@app.route('/questionnaire_of_cadets', methods=['GET', 'POST'])
@login_required
def questionnaire_of_cadets():
    if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
        log('Попытка просмотра анкет кадетов (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    teams = Teams.get_teams_for_voting()
    form = ChooseTeamForm()
    log('Просмотр анкет кадетов')
    if form.validate_on_submit():
        res_info = list()
        monthes_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                        'Ноябрь', 'Декабрь']
        _teams = [Teams.query.filter_by(id=int(form.team.data)).first()]
        for team in _teams:
            team_info = dict()
            team_info['title'] = team.name
            monthes = db.session.query(func.month(Questionnaire.date)) \
                .filter(Questionnaire.team_id == team.id).group_by(func.month(Questionnaire.date)).all()
            team_info['monthes'] = list()
            members = Membership.get_crew_of_team(team.id)
            for month in monthes:
                month_info = dict()
                month_info['title'] = monthes_name[month[0] - 1]
                texts = Questions.query.filter_by(type=2).all()
                month_info['graphs'] = [
                    {'text': texts[i - 1].text,
                     'src': url_for('static', filename='graphs/graph_{}_2020{}_{}.png'.format(team.id, month[0], i))}
                    for i in range(1, 6)]
                month_info['team'] = list()
                for member in members:
                    if User.check_can_be_marked(member.id):
                        user_info = dict()
                        user_info['name'] = member[1] + ' ' + member[2]
                        user_info['answers'] = list()
                        questionnaire = Questionnaire.query.filter(Questionnaire.team_id == team.id,
                                                                   Questionnaire.user_id == member[0],
                                                                   Questionnaire.type == 1,
                                                                   func.month(Questionnaire.date) == month[0]).first()
                        if questionnaire:
                            answers = QuestionnaireInfo.query.filter_by(questionnaire_id=questionnaire.id).all()
                            for answer in answers:
                                user_info['answers'].append(
                                    {'question': Questions.query.filter_by(id=answer.question_id).first().text,
                                     'answer': answer.question_answ})
                        month_info['team'].append(user_info)
                team_info['monthes'].append(month_info)
            res_info.append(team_info)
        log('Просмотр анкет команды с id {}'.format(form.team.data))
        return render_template('questionnaire/questionnaire_of_cadets.html', title='Анкеты курсантов', info=res_info,
                               access=get_access(current_user), form=form, teams=teams)
    return render_template('questionnaire/questionnaire_of_cadets.html', title='Анкеты курсантов', teams=teams,
                           form=form, access=get_access(current_user))
