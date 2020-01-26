# -*- coding: utf-8 -*-
import datetime
from app import app, db
from app.models import User, Questions, QuestionnaireInfo, Questionnaire, Membership, UserStatuses, Statuses, Axis, \
    Criterion, Voting, VotingInfo
from flask import render_template, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
from app.forms import LoginForm, SignupForm, QuestionnairePersonal, \
    QuestionnaireTeam, QuestionAdding, Teams, MemberAdding, TeamAdding
from flask_login import current_user, login_user, logout_user, login_required
import json


@app.route('/')
@app.route('/home')
@login_required
def home():
    user = {'name': User.query.filter_by(id=current_user.id).first().name}
    return render_template('homepage.html', title='KorpusToken', user=user,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user is None or not user.check_password(form.password.data):
            return render_template('login.html', tittle='Авторизация', form=form, err=True)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    if form.validate_on_submit():
        tg = form.tg_nickname.data
        if tg[0] == '@':
            tg = tg[1:]
        user = User(
            email=form.email.data,
            login=form.login.data,
            tg_nickname=tg,
            courses=form.courses.data,
            birthday=form.birthday.data,
            education='Unknown',#form.education.data,
            work_exp=form.work_exp.data,
            sex=form.sex.data,
            name=form.name.data,
            surname=form.surname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if form.participate.data:
            user_team = Membership(user_id=User.query.filter_by(email=form.email.data).first().id,
                                   team_id=form.team.data,
                                   role_id=0)#int(form.role.data))
            db.session.add(user_team)
        statuses = UserStatuses(user_id=User.query.filter_by(email=form.email.data).first().id, status_id=3)
        db.session.add(statuses)
        db.session.commit()
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('signup.html', title='Регистрация', form=form, script='signup.js')


@app.route('/questionnaire_self', methods=['GET', 'POST'])
def questionnaire_self():
    if not current_user.is_authenticated:
        return redirect('login')

    # Проверка на лимит голосования

    db_date = Questionnaire.query.filter_by(user_id=current_user.id, type=1).first()

    if db_date:
        now = datetime.datetime.now()
        td = str(now.year) + '-' + str(now.month)
        last = str(db_date.date.year) + '-' + str(db_date.date.month)
        if last == td:
            return render_template('questionnaire_error.html',
                                   responsibilities=User.dict_of_responsibilities(current_user.id),
                                   team=Membership.team_participation(current_user.id))

    form = QuestionnairePersonal()
    questions = Questions.query.filter_by(type=1)       # type=1 - вопросы 1-го типа, т. е. личные
    if form.validate_on_submit():
        membership = Membership.query.filter_by(user_id=current_user.id).first()
        if membership:
            q = Questionnaire(user_id=current_user.id,
                          team_id=membership.team_id,
                          date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                             datetime.datetime.now().day),
                          type=1)
        else:
            q = Questionnaire(user_id=current_user.id,
                              date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                                 datetime.datetime.now().day),
                              type=1)
        db.session.add(q)
        db.session.commit()
        answs = [form.qst_personal_growth.data, form.qst_controllability.data,
                 form.qst_selfcontrol.data, form.qst_strategy.data]
        i = 0

        for question in questions[:4]:
            answ = QuestionnaireInfo(question_id=question.id,
                                     questionnaire_id=Questionnaire.query.all()[-1].id,
                                     question_num=i+1,
                                     question_answ=answs[i])
            db.session.add(answ)
            i += 1
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('questionnaire_self.html', title='Личная анкета', form=form, q1=questions[0].text,
                           q2=questions[1].text, q3=questions[2].text, q4=questions[3].text,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/questionnaire_team', methods=['GET', 'POST'])
def questionnaire_team():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Проверка на лимит голосования

    db_date = Questionnaire.query.filter_by(user_id=current_user.id, type=2).first()

    if db_date:
        now = datetime.datetime.now()
        td = str(now.year) + '-' + str(now.month)
        last = str(db_date.date.year) + '-' + str(db_date.date.month)
        if last == td:
            return render_template('questionnaire_error.html',
                                   responsibilities=User.dict_of_responsibilities(current_user.id),
                                   team=Membership.team_participation(current_user.id))

    teammates = []
    lst_teammates_bd = Membership.query.filter_by(
        team_id=Membership.query.filter_by(user_id=current_user.id).first().team_id)

    for teammate in lst_teammates_bd:
        if teammate.user_id == current_user.id or not(User.check_cadet(teammate.user_id)):
            continue
        cur_user = User.query.filter_by(id=teammate.user_id).first()
        name = cur_user.name
        surname = cur_user.surname
        teammates.append({'id': teammate.user_id, 'name': '{} {}'.format(name, surname)})

    form = QuestionnaireTeam()
    questions = Questions.query.filter_by(type=2)

    if form.validate_on_submit():
        q = Questionnaire(user_id=current_user.id,
                          team_id=Membership.query.filter_by(user_id=current_user.id).first().team_id,
                          date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                             datetime.datetime.now().day),
                          type=2)

        db.session.add(q)
        db.session.commit()

        answs = [form.qst_q1.data, form.qst_q2.data, form.qst_q3.data, form.qst_q4.data, form.qst_q5.data]
        i = 0

        for question in questions[:5]:
            answ = QuestionnaireInfo(question_id=question.id,
                                     questionnaire_id=Questionnaire.query.all()[-1].id,
                                     question_num=i+1,
                                     question_answ=answs[i])
            db.session.add(answ)
            i += 1
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('questionnaire_team.html', title='Командная анкета', teammates=teammates, form=form,
                           q1=questions[0].text, q2=questions[1].text, q3=questions[2].text, q4=questions[3].text,
                           q5=questions[4].text, responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/question_adding', methods=['POST', 'GET'])
def question_adding():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    form = QuestionAdding()

    if form.validate_on_submit():
        q = Questions(type=form.question_type.data, text=form.question_form.data)
        db.session.add(q)
        db.session.commit()
        return render_template('question_adding.html', title='Конструктор вопросов', form=form, successful=True,
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))
    return render_template('question_adding.html', title='Конструктор вопросов', form=form, successful=False,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


# Решить трабл с отображением атаманов, админов и тимлидов в общем отображении участвующих в личных анкетах
@app.route('/questionnaire_progress', methods=['POST', 'GET'])
def questionnaire_progress():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

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
    if User.query.all():
        for user in User.query.all():
            if User.check_can_be_marked(user.id):
            #if UserStatuses.query.filter_by(user_id=user.id):
                #for status in UserStatuses.query.filter_by(user_id=user.id):
                   # if status.status_id == 3:
                        questionnaire['participaters'].append(user.id)
                        questionnaire['participaters_self_ids'].append(user.id)
                        questionnaire['max_particip'] += 1
                        questionnaire['all_team_particip'] += 1
                        questionnaire['participaters_team_ids'].append(user.id)

            if Questionnaire.query.filter_by(user_id=user.id, type=1):
                for qst in Questionnaire.query.filter_by(user_id=user.id, type=1):
                    if qst.date.month == datetime.datetime.now().month:
                        questionnaire['already_self'] += 1
                        questionnaire['participated_self'].append(user.id)

            if Questionnaire.query.filter_by(user_id=user.id, type=2):
                for qst in Questionnaire.query.filter_by(user_id=user.id, type=2):
                    if qst.date.month == datetime.datetime.now().month:
                        questionnaire['already_team'] += 1
                        questionnaire['participated_team'].append(user.id)

            # if Membership.query.all():
            #     membship_ids = [user_ids.user_id for user_ids in Membership.query.all()]
            #     if user.id in membship_ids:
            #         teams = [team.team_id for team in Membership.query.filter_by(user_id=user.id).all()]
            #         for t_id in teams:
            #             team = Teams.query.filter_by(id=t_id).first()
            #             if team.type and team.type==1:
            #                 questionnaire['all_team_particip'] += 1
            #                 questionnaire['participaters_team_ids'].append(user.id)

    not_participated_self_ids = [user for user in questionnaire['participaters_self_ids']
                                                           if user not in questionnaire['participated_self']]
    not_participated_self_names = [User.query.filter_by(id=user).first().name
                                                             for user in questionnaire['participaters_self_ids']
                                                             if user not in questionnaire['participated_self']]
    not_participated_self_surnames = [User.query.filter_by(id=user).first().surname
                                                                for user in questionnaire['participaters_self_ids']
                                                                if user not in questionnaire['participated_self']]
    not_participated_self_statuses = [Statuses.query.filter_by(
                                                       id=UserStatuses.query.filter_by(
                                                           user_id=user).first().status_id).first().status
                                                               for user in questionnaire['participaters_self_ids']
                                                               if user not in questionnaire['participated_self']]

    not_participated_self_info = []

    for i in range(len(not_participated_self_ids)):
        not_participated_self_info.append([not_participated_self_ids[i], not_participated_self_names[i],
                                           not_participated_self_surnames[i], not_participated_self_statuses[i]])

    not_participated_team_ids = [user for user in questionnaire['participaters_team_ids']
                                                           if user not in questionnaire['participated_team']]
    not_participated_team_names = [User.query.filter_by(id=user).first().name
                                                             for user in questionnaire['participaters_team_ids']
                                                             if user not in questionnaire['participated_team']]
    not_participated_team_surnames = [User.query.filter_by(id=user).first().surname
                                                                for user in questionnaire['participaters_team_ids']
                                                                if user not in questionnaire['participated_team']]
    not_participated_team_teams = [Teams.query.filter_by(
                                                       id=Membership.query.filter_by(user_id=user).first().team_id
                                                   ).first().name
                                                               for user in questionnaire['participaters_team_ids']
                                                               if user not in questionnaire['participated_team']]

    not_participated_team_info = []

    for i in range(len(not_participated_team_ids)):
        not_participated_team_info.append([not_participated_team_ids[i], not_participated_team_names[i],
                                           not_participated_team_surnames[i], not_participated_team_teams[i]])

    return render_template('questionnaire_progress.html', title='Прогресс анкетирования',
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id),
                           questionnaire=questionnaire, not_participated_self=not_participated_self_info,
                           not_participated_team=not_participated_team_info)


@app.route('/users_list', methods=['POST', 'GET'])
def users_list():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    info = db.session.query(User.name, User.surname, Teams.name, User.id).outerjoin(Membership, User.id == Membership.user_id)\
        .outerjoin(Teams, Teams.id == Membership.team_id).all()
    return render_template('users_list.html', title='Список пользователей', users=info,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/delete_user', methods=['GET'])
def delete_user():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))
    uid = request.args.get('uid')
    User.query.filter_by(id=uid).delete()
    Membership.query.filter_by(user_id=uid).delete()
    UserStatuses.query.filter_by(user_id=uid).delete()
    if len(Questionnaire.query.filter_by(user_id=uid).all()) > 0:
        q_list = Questionnaire.query.filter_by(user_id=uid).all()
        for q in q_list:
            QuestionnaireInfo.query.filter_by(questionnaire_id=q.id).delete()
            Questionnaire.query.filter_by(id=q.id).delete()
    if len(Voting.query.filter_by(user_id=uid).all()) > 0:
        v_list = Voting.query.filter_by(user_id=uid).all()
        for v in v_list:
            VotingInfo.query.filter_by(voting_id=v.id).delete()
            Voting.query.filter_by(id=v.id).delete()
    db.session.commit()
    return redirect('users_list')


@app.route('/teams_list', methods=['POST', 'GET'])
def teams_list():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    form = TeamAdding()
    if form.validate_on_submit():
        team = Teams(name=form.title.data)
        db.session.add(team)
        db.session.commit()
    return render_template('teams_list.html', title='Список текущих команд', form=form, teams=Teams.query.all(),
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/delete_team', methods=['GET'])
def delete_team():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))
    tid = request.args.get('tid')
    Teams.query.filter_by(id=tid).delete()
    db.session.commit()
    return redirect('teams_list')


@app.route('/teams_crew', methods=['POST', 'GET'])
def teams_crew():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    teams = Teams.query.all()
    info = list()
    for team in teams:
        info.append((team, Membership.get_crew_of_team(team.id)))
    return render_template('teams_crew.html', title='Текущие составы команд', info=info,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/edit_team', methods=['GET', 'POST'])
def edit_team():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    tid = int(request.args.get('tid'))
    form = MemberAdding()
    if form.validate_on_submit():
        new_member_id = int(form.name.data)
        if new_member_id > 0:
            new_member = Membership(user_id=new_member_id, team_id=tid)
            db.session.add(new_member)
            db.session.commit()
    title = Teams.query.filter_by(id=tid).first().name
    members = Membership.get_crew_of_team(tid)
    users = User.query.order_by(User.name).all()
    for team_member in members:
        if team_member[0] in [user.id for user in users]:
            print('yes')
            for user in users:
                if user.id == team_member[0]:
                    users.remove(user)

    return render_template('edit_team.html', title='Редактировать состав команды',
                           team_title=title, members=members, tid=tid, form=form, users=users,
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/delete_member', methods=['GET'])
def delete_member():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not User.check_admin(current_user.id):
        return render_template('gryazniy_vzlomshik.html',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    tid = request.args.get('tid')
    uid = request.args.get('uid')
    Membership.query.filter_by(team_id=tid, user_id=uid).delete()
    db.session.commit()

    return redirect('edit_team?tid=' + str(tid))


@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id)):
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    if (User.check_expert(current_user.id) + User.check_top_cadet(current_user.id)
            + User.check_tracker(current_user.id) + User.check_chieftain(current_user.id)) > 1:
        return redirect(url_for('assessment_axis'))

    if User.check_expert(current_user.id) or User.check_tracker(current_user.id):
        return redirect(url_for('assessment_team', axis_id=2))

    if User.check_top_cadet(current_user.id):
        return redirect(url_for('assessment_team', axis_id=1))

    if User.check_chieftain(current_user.id):
        return redirect(url_for('assessment_users', axis_id=3, team_id=0))

    return render_template('assessment.html', title='Оценка',
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id))


@app.route('/assessment_axis', methods=['GET', 'POST'])
def assessment_axis():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id)):
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    axises = [(axis.id, axis.name) for axis in Axis.query.all()]

    return render_template('assessment_axis.html', title='Выбор оси',
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id), axises=axises)


@app.route('/assessment_team', methods=['GET', 'POST'])
def assessment_team():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id)):
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))
    first_type_team_ids = [(team.id, team.name) for team in Teams.query.filter_by(type=1)]
    axis_id = request.args.get('axis_id')
    axis = ''
    if Axis.query.filter_by(id=axis_id).first():
        axis = Axis.query.filter_by(id=axis_id).first().name
    return render_template('assessment_team.html', title='Выбор команды',
                           responsibilities=User.dict_of_responsibilities(current_user.id),
                           team=Membership.team_participation(current_user.id),
                           team_lst=first_type_team_ids,
                           axis_id=axis_id, axis=axis)


@app.route('/assessment_users', methods=['GET', 'POST'])
def assessment_users():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id)):
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id))

    team_id = request.args.get('team_id')
    axis_id = request.args.get('axis_id')
    criterions = Criterion.query.filter_by(axis_id=axis_id).all()
    axis = Axis.query.filter_by(id=axis_id).first()
    if axis_id == '3':
        questions = Questions.query.filter_by(type=1)[1:4]
        cadets = [(user.id,
                    User.query.filter_by(id=user.id).first().name,
                    User.query.filter_by(id=user.id).first().surname)
                  for user in User.query.all() if User.check_can_be_marked(user.id)]
        answers = dict()
        for i, q in enumerate(criterions):
            answers[q.id] = list()
            for c in cadets:
                questionnaire = Questionnaire.query.filter(Questionnaire.user_id == c[0], Questionnaire.type == 1).first()
                if questionnaire:
                    answers[q.id].append(QuestionnaireInfo.query.filter(QuestionnaireInfo.question_id == questions[i].id,
                                                                        QuestionnaireInfo.questionnaire_id == questionnaire.id).first().question_answ)
                else:
                    answers[q.id].append('Нет ответа')
        return render_template('assessment_users.html', title='Оценка', answers=answers,
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id),
                               team_members=cadets, criterions=criterions, axis=axis, team_id=team_id)
    else:
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if current_user.id != member.id and User.check_cadet(member.id)]

        team = Teams.query.filter_by(id=team_id).first().name
        return render_template('assessment_users.html', title='Оценка',
                               responsibilities=User.dict_of_responsibilities(current_user.id),
                               team=Membership.team_participation(current_user.id), team_id=team_id,
                               team_members=team_members, axis=axis, criterions=criterions, team_title=team)


@app.route('/get_members_of_team', methods=['GET', 'POST'])
def get_members_of_team():
    team_id = int(request.args.get('team_id'))
    if team_id == 0:
        team_members = [(user.id,
                         User.query.filter_by(id=user.id).first().name,
                         User.query.filter_by(id=user.id).first().surname)
                        for user in User.query.all() if User.check_can_be_marked(user.id)]
    else:
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if current_user.id != member.id and User.check_cadet(member.id)]
    return jsonify({'members': team_members})


@app.route('/finish_vote', methods=['POST'])
def finish_vote():
    data = request.json
    team_id = int(data['team_id'])
    axis_id = int(data['axis'])
    results = data['results']
    voting = Voting(user_id=current_user.id, axis_id=axis_id, team_id=team_id,
                    date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                       datetime.datetime.now().day)
                    )
    db.session.add(voting)
    db.session.commit()
    voting_id = voting.id
    for i in range(len(results)):
        if not (results[i] is None):
            for j in range(3 * (axis_id - 1), 3 * (axis_id - 1) + 3):
                vote_info = VotingInfo(voting_id=voting_id, criterion_id=j + 1, cadet_id=i, mark=results[i][j])
                db.session.add(vote_info)
                db.session.commit()
    return redirect('/assessment')
