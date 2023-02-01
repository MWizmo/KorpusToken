# -*- coding: utf-8 -*-
import datetime, os, csv
from app.routes.questionnaire_routes import get_questionnaire_progress
from sqlalchemy import func
from app import app, db
from app.scripts.service import get_access, log
from app.scripts.generate_weekly_voting_xlsx import generate_weekly_voting_xlsx
from app.models import Questions, QuestionnaireInfo, Questionnaire, QuestionnaireTable, Membership, \
    UserStatuses, Axis, Criterion, Voting, VotingInfo, TopCadetsScore, TopCadetsVoting, \
    VotingTable, WeeklyVoting, WeeklyVotingMembers
from flask import render_template, redirect, url_for, request, jsonify, send_file
from app.forms import *
from flask_login import current_user, login_required


@app.route('/assessment_page')
@login_required
def assessment_page():
    flag = QuestionnaireTable.is_opened()
    return render_template('voting/assessment_page.html', title='Оценка вклада', flag=flag)


@app.route('/participate')
@login_required
def participate():
    if QuestionnaireTable.is_opened() and User.check_can_be_marked(current_user.id):
        return render_template('voting/participate.html', title='Участвовать в оценке')
    else:
        return redirect('/assessment')


@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    log('Просмотр страницы с оценкой')
    if QuestionnaireTable.is_opened() and User.check_can_be_marked(current_user.id):
        return redirect('/questionnaire_position')
        # return redirect('/questionnaire_self')
    if not VotingTable.is_opened():
        return render_template('voting/voting_progress.html', title='Оценка', access=get_access(current_user))
    if (User.check_expert(current_user.id) + User.check_top_cadet(current_user.id)
        + User.check_tracker(current_user.id) + User.check_chieftain(current_user.id) + User.check_teamlead(
                current_user.id)) == 0:
        return render_template('voting/voting_self_progress.html', title='Оценка', access=get_access(current_user),
                               not_voting=True)
    if (User.check_expert(current_user.id) + User.check_top_cadet(current_user.id)
        + User.check_tracker(current_user.id) + User.check_chieftain(current_user.id) + User.check_teamlead(
                current_user.id)) > 1:  # and (Axis.is_available(1)
        #                                                                                         or Axis.is_available(
        #         2) or Axis.is_available(3)):
        return redirect(url_for('assessment_axis'))

    if User.check_expert(current_user.id) or User.check_tracker(current_user.id) or User.check_teamlead(
            current_user.id):  # and Axis.is_available(2):
        teams_for_voting = len(Teams.get_teams_for_voting())
        if len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 2,
                                   Voting.voting_id == VotingTable.current_voting_id()).all()) >= teams_for_voting:
            return render_template('voting/assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        return redirect(url_for('assessment_team', axis_id=2))

    if User.check_top_cadet(current_user.id):  # and Axis.is_available(1):
        teams_for_voting = len(Teams.get_teams_for_voting())
        if len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                   Voting.voting_id == VotingTable.current_voting_id()).all()) >= teams_for_voting:
            return render_template('voting/assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        return redirect(url_for('assessment_team', axis_id=1))

    if User.check_chieftain(current_user.id):  # and Axis.is_available(3):
        if Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                               Voting.voting_id == VotingTable.current_voting_id()).first():
            return render_template('voting/assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        else:
            return redirect(url_for('c', axis_id=3, team_id=0))

    return render_template('voting/assessment.html', title='Оценка', access=get_access(current_user))


@app.route('/assessment_axis', methods=['GET', 'POST'])
@login_required
def assessment_axis():
    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id) or User.check_teamlead(
                current_user.id)):
        log('Попытка просмотра страницы с выбором оси для оценки (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    log('Просмотр страницы с выбором оси для оценки')
    assessment = VotingTable.query.filter_by(status='Active').first()
    teams_for_voting = len(Teams.get_teams_for_voting())
    voting_num_rel = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                             Voting.voting_id == assessment.id).all())
    voting_num_bus = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 2,
                                             Voting.voting_id == assessment.id).all())
    voting_num_auth = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                                              Voting.voting_id == assessment.id).all())
    axises = [(axis.id, axis.name) for axis in Axis.query.all()]
    is_first = True if User.check_top_cadet(current_user.id) else False
    is_second = True if User.check_tracker(current_user.id) or User.check_expert(current_user.id) \
                        or User.check_teamlead(current_user.id) else False
    is_third = True if User.check_chieftain(current_user.id) else False
    return render_template('voting/assessment_axis.html', title='Оценка', is_first=is_first,
                           access=get_access(current_user), axises=axises, is_third=is_third, is_second=is_second,
                           teams_for_voting=teams_for_voting,
                           voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus,
                           voting_num_auth=voting_num_auth)


@app.route('/start_vote')
@login_required
def start_voting():
    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id) or User.check_teamlead(
                current_user.id)):
        log('Попытка начать голосование(ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    assessment = VotingTable.query.filter_by(status='Active').first()
    teams_for_voting = Teams.get_teams_for_voting()
    teams_for_voting = [t.id for t in teams_for_voting]
    if User.check_top_cadet(current_user.id):
        voting_num_rel = Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                             Voting.voting_id == assessment.id).all()
        if len(voting_num_rel) < len(teams_for_voting):
            voted_team = [row.team_id for row in voting_num_rel]
            left_teams = list(set(teams_for_voting).difference(set(voted_team)))
            if len(left_teams) == 1:
                return redirect(url_for('assessment_users', axis_id=1, team_id=left_teams[0], last=1))
            else:
                return redirect(url_for('assessment_users', axis_id=1, team_id=left_teams[0]))
    if User.check_tracker(current_user.id) or User.check_expert(current_user.id) or User.check_teamlead(
            current_user.id):
        voting_num_bus = Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 2,
                                             Voting.voting_id == assessment.id).all()
        if len(voting_num_bus) < len(teams_for_voting):
            voted_team = [row.team_id for row in voting_num_bus]
            left_teams = list(set(teams_for_voting).difference(set(voted_team)))
            if len(left_teams) == 1:
                return redirect(url_for('assessment_users', axis_id=2, team_id=left_teams[0], last=1))
            else:
                return redirect(url_for('assessment_users', axis_id=2, team_id=left_teams[0]))
    if User.check_chieftain(current_user.id):
        voting_num_auth = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                                                  Voting.voting_id == assessment.id).all())
        if voting_num_auth == 0:
            return redirect(url_for('assessment_users', axis_id=3, team_id=0))
    return redirect('assessment_axis')


@app.route('/assessment_team', methods=['GET', 'POST'])
@login_required
def assessment_team():
    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id) or User.check_teamlead(
                current_user.id)):
        log('Попытка просмотра страницы с выбором команды для оценки (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))

    axis_id = request.args.get('axis_id')
    log('Просмотр страницы с выбором команды для оценки, id оси {}'.format(axis_id))
    if int(axis_id) == 3:
        if Voting.check_on_assessment(current_user.id, 0, 3):
            return redirect(url_for('assessment_users', axis_id=3, team_id=0))
        else:
            return redirect(url_for('assessment_error'))

    first_type_teams = [(team.id, team.name) for team in Teams.get_teams_for_voting() if
                        Voting.check_on_assessment(current_user.id, team.id, int(axis_id))]
    if not first_type_teams:
        log('Ошибка при выборе команд для оценки: команды первого типа отсутствуют')
        return redirect(url_for('assessment_error'))

    axis = ''
    if Axis.query.filter_by(id=axis_id).first():
        axis = Axis.query.filter_by(id=axis_id).first().name
    return render_template('voting/assessment_team.html', title='Выбор команды',
                           access=get_access(current_user),
                           team_lst=first_type_teams,
                           axis_id=axis_id, axis=axis)


@app.route('/assessment_users', methods=['GET', 'POST'])
@login_required
def assessment_users():
    if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
            or User.check_expert(current_user.id) or User.check_chieftain(current_user.id) or User.check_teamlead(
                current_user.id)):
        log('Попытка просмотра страницы с оценкой пользователей (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    # q_ids = []

    assessment = VotingTable.query.filter_by(status='Active').first()
    teams_for_voting = len(Teams.get_teams_for_voting())
    voting_num_rel = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                             Voting.voting_id == assessment.id).all())
    voting_num_bus = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 2,
                                             Voting.voting_id == assessment.id).all())
    voting_num_auth = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                                              Voting.voting_id == assessment.id).all())
    axises = [(axis.id, axis.name) for axis in Axis.query.all()]
    is_first = True if User.check_top_cadet(current_user.id) else False
    is_second = True if User.check_tracker(current_user.id) or User.check_expert(current_user.id) \
                        or User.check_teamlead(current_user.id) else False
    is_third = True if User.check_chieftain(current_user.id) else False

    team_id = int(request.args.get('team_id'))
    axis_id = request.args.get('axis_id')
    log('Просмотр страницы с оценкой по оси id {} команды с id {}'.format(axis_id, team_id))
    criterions = Criterion.query.filter_by(axis_id=axis_id).all()
    axis = Axis.query.filter_by(id=axis_id).first()
    q_id = QuestionnaireTable.query.filter_by(status='Ready for assessment').first().id
    if axis_id == '3':
        questions = Questions.query.filter_by(type=1)[1:4]
        cadets = [(user.id,
                   User.query.filter_by(id=user.id).first().name,
                   User.query.filter_by(id=user.id).first().surname)
                  for user in User.query.all() if User.check_can_be_marked(user.id) and current_user.id != user.id]
        answers = dict()
        for i, q in enumerate(criterions):
            answers[q.id] = list()
            for c in cadets:
                questionnaire = Questionnaire.query.filter(Questionnaire.questionnaire_id == q_id,
                                                           Questionnaire.user_id == c[0], Questionnaire.type == 1).all()
                if questionnaire:
                    # q_ids.append(questionnaire.id)
                    questionnaire = questionnaire[-1]
                    answers[q.id].append(
                        QuestionnaireInfo.query.filter(QuestionnaireInfo.question_id == questions[i].id,
                                                       QuestionnaireInfo.questionnaire_id == questionnaire.id).first().question_answ)
                else:
                    answers[q.id].append('Нет ответа')
        return render_template('voting/authority_voting.html', title='Ось власти', answers=answers,
                               access=get_access(current_user), questions=questions,
                               team_members=cadets, criterions=criterions, axis=axis, team_id=team_id,
                               is_first=is_first,
                               is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                               voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus,
                               voting_num_auth=voting_num_auth)
    elif axis_id == '2':
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if User.check_cadet(member.user_id)]
        # if current_user.id != member.user_id and User.check_cadet(member.user_id)]
        team = Teams.query.filter_by(id=team_id).first().name
        # current_month = datetime.datetime.now().month
        monthes = [5, 6, 7, 8, 9, 10, 11, 12]
        dates = []
        for current_month in monthes:
            dates += db.session.query(WeeklyVoting.date).filter(func.month(WeeklyVoting.date) == current_month,
                                                                WeeklyVoting.team_id == team_id,
                                                                WeeklyVoting.finished == 1).distinct().all()

        voting_results = []
        voting_dict = {}
        for user in team_members:
            voting_dict[user[0]] = {'name': f'{user[1]} {user[2]}', 'marks1': [], 'marks2': [], 'marks3': [],
                                    'marks1_1': 0, 'marks1_0': 0, 'marks2_1': 0, 'marks2_0': 0, 'marks3_1': 0,
                                    'marks3_0': 0}
        dates_str = []
        for date in dates:
            date_info = {'date': f'{date[0].day}.{date[0].month}.{date[0].year}'}
            dates_str.append(f'{date[0].day}.{date[0].month}.{date[0].year}')
            marks = db.session.query(WeeklyVoting.criterion_id, func.avg(WeeklyVoting.mark)). \
                filter(WeeklyVoting.date == date[0], WeeklyVoting.team_id == team_id, WeeklyVoting.finished == 1). \
                group_by(WeeklyVoting.criterion_id).all()
            mark_res = []
            for mark in marks:
                mark_res.append({'criterion': Criterion.query.get(mark[0]).name, 'mark': 1 if mark[1] == 1 else 0})
            if len(marks) == 0:
                mark_res = [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0},
                            {'criterion': 'Подтверждение средой', 'mark': 0}]
            date_info['marks'] = mark_res
            teammates = db.session.query(WeeklyVotingMembers.cadet_id).filter(WeeklyVotingMembers.date == date[0],
                                                                              WeeklyVotingMembers.team_id == team_id).all()
            if len(teammates) == 0:
                teammates = [user_id for user_id in voting_dict]
            else:
                teammates = [t[0] for t in teammates]

            for user in voting_dict:
                if user in teammates and mark_res[0]['mark'] == 1:
                    voting_dict[user]['marks1'].append(1)
                    voting_dict[user]['marks1_1'] += 1
                else:
                    voting_dict[user]['marks1'].append(0)
                    voting_dict[user]['marks1_0'] += 1
                if user in teammates and mark_res[1]['mark'] == 1:
                    voting_dict[user]['marks2'].append(1)
                    voting_dict[user]['marks2_1'] += 1
                else:
                    voting_dict[user]['marks2'].append(0)
                    voting_dict[user]['marks2_0'] += 1
                if user in teammates and mark_res[2]['mark'] == 1:
                    voting_dict[user]['marks3'].append(1)
                    voting_dict[user]['marks3_1'] += 1
                else:
                    voting_dict[user]['marks3'].append(0)
                    voting_dict[user]['marks3_0'] += 1
            teammates_info = []
            for member in team_members:
                if member[0] in teammates and len(teammates) > 0:
                    teammates_info.append(member)
                elif len(teammates) == 0:
                    teammates_info.append(member)
            date_info['teammates'] = teammates_info
            voting_results.append(date_info)
        return render_template('voting/business_voting.html', title='Ось дела',
                               access=get_access(current_user), team_id=team_id, voting_results=voting_results,
                               dates=dates_str,
                               team_members=team_members, axis=axis, criterions=criterions, team_title=team,
                               voting_dict=voting_dict, is_first=is_first,
                               is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                               voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus,
                               voting_num_auth=voting_num_auth)
    else:
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if current_user.id != member.user_id and User.check_cadet(member.user_id)]
        question = Questions.query.filter_by(type=1).first()
        answers = list()
        for member in team_members:
            questionnaire = Questionnaire.query.filter(Questionnaire.questionnaire_id == q_id,
                                                       Questionnaire.user_id == member[0],
                                                       Questionnaire.type == 1).all()
            if questionnaire:
                # q_ids.append(questionnaire.id)
                questionnaire = questionnaire[-1]
                answers.append(QuestionnaireInfo.query.filter(QuestionnaireInfo.question_id == question.id,
                                                              QuestionnaireInfo.questionnaire_id == questionnaire.id).first().question_answ)
            else:
                answers.append('Нет ответа')
        texts = Questions.query.filter_by(type=2).all()
        images = [
            {'text': texts[i - 1].text, 'src': url_for('static',
                                                       filename='graphs/graph_{}_{}_{}.png'.format(team_id, q_id, i))}
            for i in range(1, 6)]
        team = Teams.query.filter_by(id=team_id).first().name
        is_last = 1 if 'last' in request.args else 0
        return render_template('voting/relations_voting.html', title='Ось отношений', answers=answers, images=images,
                               access=get_access(current_user), team_id=team_id,  # q_ids=q_ids,
                               team_members=team_members, axis=axis, criterions=criterions, team_title=team,
                               is_first=is_first, is_last=is_last, voting_num_auth=voting_num_auth,
                               is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                               voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus)


@app.route('/business_details/<team_id>/<uid>')
@login_required
def business_details(team_id, uid):
    monthes = [5, 6, 7, 8, 9, 10, 11, 12]
    dates = []
    for current_month in monthes:
        dates += db.session.query(WeeklyVoting.date).filter(func.month(WeeklyVoting.date) == current_month,
                                                            WeeklyVoting.team_id == team_id,
                                                            WeeklyVoting.finished == 1).distinct().all()

    voting_dict = {'name': User.get_full_name(uid), 'marks1': [], 'marks2': [], 'marks3': []}
    dates_str = []
    for date in dates:
        dates_str.append(f'{date[0].day}.{date[0].month}.{date[0].year}')
        marks = db.session.query(WeeklyVoting.criterion_id, func.avg(WeeklyVoting.mark)). \
            filter(WeeklyVoting.date == date[0], WeeklyVoting.team_id == team_id, WeeklyVoting.finished == 1). \
            group_by(WeeklyVoting.criterion_id).all()
        mark_res = []
        for mark in marks:
            mark_res.append({'criterion': Criterion.query.get(mark[0]).name, 'mark': 1 if mark[1] == 1 else 0})
        if len(marks) == 0:
            mark_res = [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0},
                        {'criterion': 'Подтверждение средой', 'mark': 0}]
        if mark_res[0]['mark'] == 1:
            voting_dict['marks1'].append(1)
        else:
            voting_dict['marks1'].append(0)
        if mark_res[1]['mark'] == 1:
            voting_dict['marks2'].append(1)
        else:
            voting_dict['marks2'].append(0)
        if mark_res[2]['mark'] == 1:
            voting_dict['marks3'].append(1)
        else:
            voting_dict['marks3'].append(0)
    return render_template('voting/business_details.html', title='Ось дела - Подробнее',
                           access=get_access(current_user), voting_results=voting_dict, dates=dates_str)

@app.route('/finish_vote', methods=['POST'])
def finish_vote():
    data = request.json
    team_id = int(data['team_id'])
    axis_id = int(data['axis'])
    results = data['results']
    is_last = int(data['is_last'])
    voting = Voting(user_id=current_user.id, axis_id=axis_id, team_id=team_id,
                    date=datetime.date(datetime.datetime.now().year, datetime.datetime.now().month,
                                       datetime.datetime.now().day), voting_id=VotingTable.current_voting_id())
    db.session.add(voting)
    db.session.commit()
    voting_id = voting.id
    for i in range(len(results)):
        if not (results[i] is None):
            for j in range(3 * (axis_id - 1), 3 * (axis_id - 1) + 3):
                vote_info = VotingInfo(voting_id=voting_id, criterion_id=j + 1, cadet_id=i, mark=results[i][j])
                db.session.add(vote_info)
                db.session.commit()
    # for q_id in q_ids:
    #     questionnaire = Questionnaire.query.filter_by(id=q_id).first()
    #     questionnaire.assessment = 0
    #     db.session.commit()

    log('Завершение оценки по оси c id {} команды с id {}'.format(axis_id, team_id))
    if is_last:
        return redirect(url_for('voting_summary', axis_id=axis_id))
    else:
        return redirect(url_for('assessment'))


@app.route('/voting_summary')
def voting_summary():
    axis_id = int(request.args.get('axis_id'))
    assessment = VotingTable.query.filter_by(status='Active').first()
    voting_num_rel = Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == axis_id,
                                         Voting.voting_id == assessment.id).all()
    voted_team = [row.team_id for row in voting_num_rel]
    voting_info = {}
    for t in voted_team:
        cur_voting = Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == axis_id,
                                         Voting.voting_id == assessment.id, Voting.team_id == t).first()
        team_members = [(member.user_id, User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=t) if User.check_cadet(member.user_id)]
        voting_dict = {}
        for user in team_members:
            marks = VotingInfo.query.filter(VotingInfo.voting_id == cur_voting.id, VotingInfo.cadet_id == user[0]).all()
            voting_dict[user[0]] = {'name': f'{user[1]} {user[2]}'}
            for mark in marks:
                voting_dict[user[0]][Criterion.query.get(mark.criterion_id).name] = mark.mark
        voting_info[Teams.query.get(t).name] = {'id': t, 'marks': voting_dict}
    teams_for_voting = len(Teams.query.filter_by(type=1).all())
    voting_num_rel = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                             Voting.voting_id == assessment.id).all())
    voting_num_bus = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 2,
                                             Voting.voting_id == assessment.id).all())
    voting_num_auth = len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                                              Voting.voting_id == assessment.id).all())
    axises = [(axis.id, axis.name) for axis in Axis.query.all()]
    is_first = True if User.check_top_cadet(current_user.id) else False
    is_second = True if User.check_tracker(current_user.id) or User.check_expert(current_user.id) \
                        or User.check_teamlead(current_user.id) else False
    is_third = True if User.check_chieftain(current_user.id) else False
    return render_template('voting/voting_summary.html', voting_info=voting_info, is_first=is_first,
                           is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                           voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus,
                           voting_num_auth=voting_num_auth, criterions=Criterion.query.filter_by(axis_id=axis_id).all())


@app.route('/start_assessment')
def start_assessment():
    if not (User.check_admin(current_user.id)):
        log('Попытка открыть оценку (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    assessment_status = VotingTable(status='Active')
    db.session.add(assessment_status)
    db.session.commit()
    log('Открыл оценку')
    return redirect('voting_progress')


@app.route('/finish_assessment')
def finish_assessment():
    if not (User.check_admin(current_user.id)):
        log('Попытка закрыть оценку (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    cur_voting = VotingTable.query.filter_by(status='Active').first()
    voting_id = cur_voting.id
    filename = 'results_' + str(voting_id) + '.csv'
    with open(os.path.join(app.root_path + '/results', filename), 'w') as output:
        writer = csv.writer(output, delimiter=';')
        criterions = [c.name for c in Criterion.query.all()]
        writer.writerow([' '] + criterions)
        users = [(user.id, user.name + ' ' + user.surname) for user in User.query.all() if
                 User.check_can_be_marked(user.id)]
        for user in users:
            res = [user[1]]
            user_res = db.session.query(func.avg(VotingInfo.mark)).outerjoin(Voting,
                                                                             Voting.id == VotingInfo.voting_id).filter(
                Voting.voting_id == voting_id, VotingInfo.cadet_id == user[0]).group_by(
                VotingInfo.criterion_id).all()
            for mark in user_res:
                if float(mark[0]) < 1.0:
                    res.append(0)
                else:
                    res.append(1)
            writer.writerow(res)
    if cur_voting:
        q = QuestionnaireTable.query.filter_by(status='Ready for assessment').first()
        q.status = 'Finished'
        cur_voting.status = 'Fixed'
        db.session.commit()
        log('Закрыл оценку')

    q_ids = [questionnaire.id for questionnaire in Questionnaire.query.filter_by(assessment=1).all()]
    for q_id in q_ids:
        questionnaire = Questionnaire.query.filter_by(id=q_id).first()
        questionnaire.assessment = 0
        db.session.commit()

    return redirect('questionnaire_progress')


@app.route('/assessment_error', methods=['GET'])
def assessment_error():
    log('Ошибка при оценке')
    return render_template('voting/assessment_error.html', title='Лимит исчерпан', access=get_access(current_user))


@app.route('/voting_progress', methods=['GET', 'POST'])
@login_required
def voting_progress():
    log('Просмотр страницы с прогрессом оценки')
    is_opened = QuestionnaireTable.is_opened()
    if is_opened:
        counter, questionnaire, not_participated_team_info, not_participated_self_info = get_questionnaire_progress()
        return render_template('voting/voting_progress.html', title='Прогресс голосования',
                               access=get_access(current_user), counter=counter, q=True,
                               questionnaire=questionnaire, not_participated_self=not_participated_self_info,
                               not_participated_team=not_participated_team_info)
    assessment = VotingTable.query.filter_by(status='Active').first()
    if assessment:
        top_cadets = [user.user_id for user in UserStatuses.query.filter_by(status_id=7).all()]
        trackers = [user.user_id for user in UserStatuses.query.filter_by(status_id=5).all()]
        for user in UserStatuses.query.filter_by(status_id=4).all():
            if user.user_id not in trackers:
                trackers.append(user.user_id)
        atamans = [user.user_id for user in UserStatuses.query.filter_by(status_id=2).all()]
        teams_for_voting = len(Teams.get_teams_for_voting())
        relation_results = list()
        for cadet_id in top_cadets:
            cadet = User.query.filter_by(id=cadet_id).first()
            if cadet:
                voting_num = len(Voting.query.filter(Voting.user_id == cadet_id, Voting.axis_id == 1,
                                                     Voting.voting_id == assessment.id).all())
                relation_results.append(('{} {}'.format(cadet.name, cadet.surname), voting_num))

        business_results = list()
        for user_id in trackers:
            user = User.query.filter_by(id=user_id).first()
            if user:
                voting_num = len(Voting.query.filter(Voting.user_id == user_id, Voting.axis_id == 2,
                                                     Voting.voting_id == assessment.id).all())
                business_results.append(('{} {}'.format(user.name, user.surname), voting_num))

        authority_results = list()
        for user_id in atamans:
            user = User.query.filter_by(id=user_id).first()
            if user:
                voting_num = len(Voting.query.filter(Voting.user_id == user_id, Voting.axis_id == 3,
                                                     Voting.voting_id == assessment.id).all())
                authority_results.append(('{} {}'.format(user.name, user.surname), voting_num))
        form = StartAssessmentForm()
        if form.validate_on_submit():
            assessment_status = VotingTable(status='Active', month=form.month.data)
            db.session.add(assessment_status)
            db.session.commit()
            log('Открыл оценку')
            return redirect('voting_progress')
        return render_template('voting/voting_progress.html', title='Прогресс голосования',
                               access=get_access(current_user),
                               teams_number=teams_for_voting, relation=relation_results,
                               business=business_results, authority=authority_results, form=form)  # ,
        # rel_text=rel_text, bus_text=bus_text, auth_text=auth_text)
    else:
        form = StartAssessmentForm()
        if form.validate_on_submit():
            if QuestionnaireTable.is_opened():
                return render_template('voting/voting_progress.html', title='Прогресс голосования',
                                       access=get_access(current_user), form=form,
                                       msg='Сначала надо завершить текущий процесс анкетирования')
            assessment_status = VotingTable(status='Active', month=form.month.data)
            db.session.add(assessment_status)
            db.session.commit()
            log('Открыл оценку')
            return redirect('voting_progress')
        return render_template('voting/voting_progress.html', title='Прогресс голосования',
                               access=get_access(current_user), form=form)


@app.route('/axis_access')
@login_required
def axis_access():
    if not User.check_admin(current_user.id):
        log('Попытка открытия или закрытия оси для оценки (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))
    axis_id = int(request.args.get('axis_id'))
    axis = Axis.query.filter_by(id=axis_id).first()
    axis.is_opened = abs(axis.is_opened - 1)
    db.session.commit()
    if axis.is_opened:
        log('Открытие оси с id {} для оценки'.format(axis_id))
    else:
        log('Закрытие оси с id {} для оценки'.format(axis_id))
    return redirect('voting_progress')


@app.route('/sum_up_assessment', methods=['GET', 'POST'])
@login_required
def sum_up_assessment():
    # if not (User.check_admin(current_user.id)):
    #     log('Попытка подведения результатов оценки (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
    #                            access=get_access(current_user))
    cur_voting = VotingTable.query.filter_by(status='Active').first()
    if cur_voting:
        voting_id = cur_voting.id
    else:
        voting_id = VotingTable.query.filter_by(status='Finished').all()[-1].id
    filename = 'results_' + str(voting_id) + '.csv'
    with open(os.path.join(app.root_path + '/results', filename), 'w') as output:
        writer = csv.writer(output, delimiter=';')
        criterions = [c.name for c in Criterion.query.all()]
        writer.writerow([' '] + criterions)
        users = [(user.id, user.name + ' ' + user.surname) for user in User.query.all() if
                 User.check_can_be_marked(user.id)]
        for user in users:
            res = [user[1]]
            user_res = db.session.query(func.avg(VotingInfo.mark)).outerjoin(Voting,
                                                                             Voting.id == VotingInfo.voting_id).filter(
                Voting.voting_id == voting_id, VotingInfo.cadet_id == user[0]).group_by(
                VotingInfo.criterion_id).all()
            for mark in user_res:
                if float(mark[0]) < 1.0:
                    res.append(0)
                else:
                    res.append(1)
            writer.writerow(res)
    log('Подведение результатов оценки')
    return redirect(url_for('assessment_results'))


@app.route('/get_assessment_results', methods=['GET'])
@login_required
def get_assessment_results():
    cur_voting = VotingTable.query.filter_by(status='Active').first()
    if cur_voting:
        voting_id = cur_voting.id
    else:
        voting_id = VotingTable.query.filter_by(status='Finished').all()[-1].id
    filename = 'results_' + str(voting_id) + '.csv'
    log('Скачивание файла с результатом оценки')
    return send_file(os.path.join(app.root_path + '/results', filename),
                     as_attachment=True, attachment_filename=filename, mimetype='text/csv')


@app.route('/assessment_results', methods=['GET'])
@login_required
def assessment_results():
    votings = VotingTable.query.all()
    return render_template('voting/assessment_results.html', title='Результаты оценки',
                           access=get_access(current_user), votings=votings)
    cur_voting = VotingTable.query.filter_by(status='Active').first()
    if cur_voting:
        voting_id = cur_voting.id
    else:
        voting_id = VotingTable.query.filter_by(status='Finished').all()[-1].id
    filename = 'results_' + str(voting_id) + '.csv'
    log('Просмотр страницы результатов')
    if os.path.isfile(os.path.join(app.root_path + '/results', filename)):
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
        return render_template('voting/assessment_results.html', title='Результаты оценки',
                               access=get_access(current_user),
                               criterions=criterions, info=user_info)
    else:
        return render_template('voting/assessment_results.html', title='Результаты оценки',
                               access=get_access(current_user))


@app.route('/weekly_results', methods=['GET'])
@login_required
def weekly_results():
    votings = WeeklyVoting.query.group_by(WeeklyVoting.date).all()
    for v in votings:
        day = f'0{v.date.day}' if v.date.day < 10 else v.date.day
        month = f'0{v.date.month}' if v.date.month < 10 else v.date.month
        v.date_str = f'{day}.{month}.{v.date.year}'
        v.date = f'{v.date.year}-{v.date.month}-{v.date.day}'
    return render_template('voting/weekly_results.html', title='Результаты еженедельной оценки',
                           access=get_access(current_user), votings=votings[::-1])


@app.route('/get_results_of_voting', methods=['GET'])
@login_required
def get_results_of_voting():
    voting_id = int(request.args.get('voting_id'))
    filename = 'results_' + str(voting_id) + '.csv'
    log('Просмотр страницы результатов')
    if os.path.isfile(os.path.join(app.root_path + '/results', filename)):
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
        return jsonify({'criterions': criterions, 'user_info': user_info})
    else:
        return jsonify({'criterions': None, 'user_info': None})


@app.route('/get_results_of_weekly_voting', methods=['GET'])
@login_required
def get_results_of_weekly_voting():
    date = request.args.get('voting_date')
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    teams = [t for t in Teams.query.all() if t.type in [1, 4]]
    summary_results = []
    for t in teams:
        team_members = [(member.user_id, User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=t.id) if User.check_cadet(member.user_id)]
        voting_results = []
        date_info = {'date': f'{date.day}.{date.month}.{date.year}'}
        teammates = db.session.query(WeeklyVotingMembers.cadet_id).filter(WeeklyVotingMembers.date == date,
                                                                          WeeklyVotingMembers.team_id == t.id).all()

        if len(teammates) == 0:
            teammates = [user[0] for user in team_members]
        else:
            teammates = [t[0] for t in teammates]
        marks = db.session.query(
            WeeklyVoting.criterion_id,
            WeeklyVoting.user_id,
            func.avg(WeeklyVoting.mark)
        ) \
            .filter(WeeklyVoting.date == date, WeeklyVoting.team_id == t.id, WeeklyVoting.finished == 1,
                    WeeklyVoting.user_id.in_(teammates)) \
            .group_by(WeeklyVoting.criterion_id, WeeklyVoting.user_id, WeeklyVoting.date) \
            .all()

        mark_res = {teammate: {date: [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0},
                                      {'criterion': 'Подтверждение средой', 'mark': 0}]} for teammate in teammates}
        for mark in marks:
            teammate_mark_res = mark_res.get(mark[1])
            if teammate_mark_res is not None:
                criterion = next(criterion for criterion in teammate_mark_res.get(date) if
                                 criterion['criterion'] == Criterion.query.get(mark[0]).name)
                criterion['mark'] = 1 if mark[2] >= 0.5 else 0
        date_info['marks'] = mark_res

        voting_list = []

        for user in team_members:
            row = {'name': f'{user[1]} {user[2]}', 'marks1': [], 'marks2': [], 'marks3': []}
            row['voting_date'] = date

            if user[0] in teammates and mark_res[user[0]][date][0]['mark'] == 1:
                row['marks1'].append(1)
            else:
                row['marks1'].append(0)
            if user[0] in teammates and mark_res[user[0]][date][1]['mark'] == 1:
                row['marks2'].append(1)
            else:
                row['marks2'].append(0)
            if user[0] in teammates and mark_res[user[0]][date][2]['mark'] == 1:
                row['marks3'].append(1)
            else:
                row['marks3'].append(0)

            voting_list.append(row)

        teammates_info = []
        for member in team_members:
            if member[0] in teammates and len(teammates) > 0:
                teammates_info.append(member)
            elif len(teammates) == 0:
                teammates_info.append(member)
        date_info['teammates'] = teammates_info
        voting_results.append(date_info)
        summary_results.append({'team': t.name, 'marks': voting_list})

    table_name = f"weekly_voting_{date.year}.{date.month}.{date.day}.xlsx"
    generate_weekly_voting_xlsx(table_name, summary_results)

    return {'results': summary_results, 'table_path': url_for('static', filename=f"weekly_votings/{table_name}")}


@app.route('/send_results_of_weekly_voting')
def send_results_of_weekly_voting():
    votings = WeeklyVoting.query.group_by(WeeklyVoting.date).all()
    date = votings[-1].date
    # date = datetime.datetime.strptime(date, '%Y-%m-%d')
    teams = [t for t in Teams.query.all() if t.type in [1, 4]]
    summary_results = []
    k = 0
    for t in teams:
        team_members = [(member.user_id, User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=t.id) if User.check_cadet(member.user_id)]
        voting_results = []
        voting_dict = {}
        for user in team_members:
            voting_dict[user[0]] = {'name': f'{user[1]} {user[2]}', 'marks1': [], 'marks2': [], 'marks3': [],
                                    'user_id': user[0]}
        dates_str = []

        date_info = {'date': f'{date.day}.{date.month}.{date.year}'}
        dates_str.append(f'{date.day}.{date.month}.{date.year}')
        marks = db.session.query(WeeklyVoting.criterion_id, func.avg(WeeklyVoting.mark)). \
            filter(WeeklyVoting.date == date, WeeklyVoting.team_id == t.id, WeeklyVoting.finished == 1). \
            group_by(WeeklyVoting.criterion_id).all()
        mark_res = []
        for mark in marks:
            mark_res.append({'criterion': Criterion.query.get(mark[0]).name, 'mark': 1 if mark[1] >= 0.5 else 0})
        if len(marks) == 0:
            mark_res = [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0},
                        {'criterion': 'Подтверждение средой', 'mark': 0}]
        date_info['marks'] = mark_res
        teammates = db.session.query(WeeklyVotingMembers.cadet_id).filter(WeeklyVotingMembers.date == date,
                                                                          WeeklyVotingMembers.team_id == t.id).all()
        if len(teammates) == 0:
            teammates = [user_id for user_id in voting_dict]
        else:
            teammates = [t[0] for t in teammates]
        for user in voting_dict:
            if user in teammates and mark_res[0]['mark'] == 1:
                voting_dict[user]['marks1'].append(1)
            else:
                voting_dict[user]['marks1'].append(0)
            if user in teammates and mark_res[1]['mark'] == 1:
                voting_dict[user]['marks2'].append(1)
            else:
                voting_dict[user]['marks2'].append(0)
            if user in teammates and mark_res[2]['mark'] == 1:
                voting_dict[user]['marks3'].append(1)
            else:
                voting_dict[user]['marks3'].append(0)
        teammates_info = []
        for member in team_members:
            if member[0] in teammates and len(teammates) > 0:
                teammates_info.append(member)
            elif len(teammates) == 0:
                teammates_info.append(member)
        date_info['teammates'] = teammates_info
        voting_results.append(date_info)
        summary_results.append({'team': t.name, 'marks': voting_dict, 'team_id': t.id})
    return jsonify({'results': summary_results, 'date': f'{date.day}.{date.month}.{date.year}'})


@app.route('/choose_top_cadets', methods=['GET'])
@login_required
def choose_top_cadets():
    log('Просмотр страницы с выбором топовых кадетов')
    cur_voting = QuestionnaireTable.current_questionnaire_id()
    if TopCadetsVoting.query.filter(TopCadetsVoting.voting_id == cur_voting,
                                    TopCadetsVoting.voter_id == current_user.id).first():
        return render_template('voting/top_cadets_error.html', title='Выбор оценивающих по оси отношений',
                               access=get_access(current_user))
    cadets = list()
    for user in User.query.all():
        if User.check_cadet(user.id):
            if user.photo:
                cadets.append((user.id, app.root_path + '/static/user_photos/user' + str(user.id) + '.jpg',
                               user.name + ' ' + user.surname))
            else:
                cadets.append((user.id, None, user.name + ' ' + user.surname))
    # cadets = [user for user in User.query.all() if User.check_cadet(user.id)]

    return render_template('voting/choose_top_cadets.html', title='Выбор оценивающих по оси отношений',
                           access=get_access(current_user),
                           cadets=cadets)


@app.route('/confirm_top_cadets', methods=['POST'])
def confirm_top_cadets():
    data = request.json
    cadets = data['top_cadets']
    for cadet in cadets:
        score = TopCadetsScore.query.filter_by(user_id=cadet).first()
        if score:
            score.score += 1
        else:
            score = TopCadetsScore(user_id=cadet, score=1)
            db.session.add(score)
    db.session.commit()
    UserStatuses.query.filter_by(status_id=7).delete()
    top_cadets = TopCadetsScore.query.order_by(TopCadetsScore.score.desc()).all()[:5]
    for cadet in top_cadets:
        us = UserStatuses(user_id=cadet.user_id, status_id=7)
        db.session.add(us)
    new_voting = TopCadetsVoting(voter_id=current_user.id, date=datetime.date(datetime.datetime.now().year,
                                                                              datetime.datetime.now().month,
                                                                              datetime.datetime.now().day),
                                 voting_id=QuestionnaireTable.current_questionnaire_id())
    db.session.add(new_voting)
    db.session.commit()
    log('Выбор топовых кадетов')
    return jsonify({'response': 'ok'})
