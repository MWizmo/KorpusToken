# -*- coding: utf-8 -*-
import datetime, os, csv, requests
from app.routes.questionnaire_routes import get_questionnaire_progress
from sqlalchemy import func, or_, and_
from sqlalchemy.sql import text
from app import app, db, w3, ktd_address, contract_address, ETH_IN_WEI, KT_BITS_IN_KT
from web3.auto import Web3
from app.scripts.service import get_access, log
from app.scripts.generate_weekly_voting_xlsx import generate_weekly_voting_xlsx
from app.models import SkillKeyword, User, Questions, QuestionnaireInfo, Questionnaire, QuestionnaireTable, Membership, \
    UserStatuses, Statuses, Axis, Criterion, Voting, VotingInfo, TeamRoles, Log, TopCadetsScore, TopCadetsVoting, \
    VotingTable, WeeklyVoting, WeeklyVotingMembers, BudgetRecord, Transaction, EthExchangeRate, TokenExchangeRate, \
    Profit, KorpusServices, ServicePayments, Budget, Skill, WorkExperience, Language
from flask import render_template, redirect, url_for, request, jsonify, send_file, flash
from werkzeug.urls import url_parse
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from app import token_utils
import math
import json
from dateutil import parser
from dateutil.relativedelta import relativedelta
import html


@app.route('/')
@app.route('/home')
@login_required
def home():
    log('Просмотр главной страницы')
    # user = {'name': User.query.filter_by(id=current_user.id).first().name}
    # message = 'В настоящее время функционал портала ограничен. Очень скоро здесь появится всё то, чего ' \
    #           'мы все так давно ждали!  '
    # cur_voting = VotingTable.query.filter_by(status='Finished').all()
    # if cur_voting:
    #     voting_id = cur_voting[-1].id
    #     month = cur_voting[-1].month
    #     filename = 'results_' + str(voting_id) + '.csv'
    #     if os.path.isfile(os.path.join(app.root_path + '/results', filename)):
    #         user_info = list()
    #         with open(os.path.join(app.root_path + '/results', filename)) as file:
    #             reader = csv.reader(file)
    #             next(reader)
    #             for row in reader:
    #                 user_marks = row[0].split(';')
    #                 user_marks.append(sum(int(item) for item in row[0].split(';')[1:]))
    #                 user_info.append(user_marks)
    #         user_info.sort(key=lambda i: i[-1], reverse=True)
    #         criterions = [c.name for c in Criterion.query.all()]
    #         message = message[:-1] + 'А пока вы можете посмотреть результаты оценки вклада за {}.'.format(month)
    #         return render_template('homepage.html', title='KorpusToken', user=user,
    #                                access=get_access(current_user),
    #                                criterions=criterions, info=user_info, message=message, flag=True)
    return render_template('homepage.html', title='KorpusToken', access=get_access(current_user))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация')
    else:
        values = request.values
        user = User.query.filter_by(login=values['login']).first()
        if user is None or not user.check_password(values['password']):
            return render_template('login.html', tittle='Авторизация', err=True)
        login_user(user, remember='remember' in values)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        log('Вход в систему')
        return redirect(next_page)


@app.route('/restore_password', methods=['GET', 'POST'])
def restore_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RestorePassword()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль успешно сменен', 'restore')
        log('Восстановления пароля', user_id=user.id)
        return redirect('login')
    return render_template('restore_password.html', title='Восстановление пароля', form=form)


@app.route('/partner')
def partner():
    return render_template('signup.html', title='Регистрация', script='signup.js', for_partner=True)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'GET':
        return render_template('signup.html', title='Регистрация', script='signup.js')
    else:
        values = request.values
        tg = values['tlg']
        if tg[0] == '@':
            tg = tg[1:]
        ethAccount = w3.eth.account.create()
        user = User(
            email='',
            login=values['login'],
            tg_nickname=tg,
            courses='',
            birthday='',
            education='Unknown',  # form.education.data,
            work_exp='',
            sex='',
            name=values['first_name'],
            surname=values['surname'],
            private_key=ethAccount.privateKey.hex())
        user.set_password(values['password'])
        db.session.add(user)
        db.session.commit()
        if values['is_partner'] == '0':
            statuses = UserStatuses(user_id=user.id, status_id=3)
        else:
            statuses = UserStatuses(user_id=user.id, status_id=10)
        db.session.add(statuses)
        db.session.commit()
        return render_template('after_register.html', title='Регистрация', name=values['first_name'])


@app.route('/logout')
def logout():
    log('Выход из системы')
    logout_user()
    return redirect(url_for('home'))


@app.route('/users_list', methods=['POST', 'GET'])
@login_required
def users_list():
    # if not User.check_admin(current_user.id):
    #     log('Попытка просмотра страницы со списком пользователей (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            access=get_access(current_user))
    log('Просмотр страницы со списком пользователей')
    users = User.query.all()
    info = list()
    for user in users:
        teams = Membership.query.filter_by(user_id=user.id).all()
        if teams:
            user_teams = [team.name for t in teams for team in Teams.query.filter_by(id=t.team_id).all()]
            info.append((user.name, user.surname, ', '.join(user_teams), user.id, user.tg_id, user.level))
        else:
            info.append((user.name, user.surname, 'Нет', user.id, user.tg_id, user.level))

    return render_template('users_list.html', title='Список пользователей', users=info,
                           access=get_access(current_user))


@app.route('/delete_user', methods=['GET'])
@login_required
def delete_user():
    if not User.check_admin(current_user.id):
        log('Попытка удалить пользователя (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))
    uid = request.args.get('uid')
    user = User.query.filter_by(id=current_user.id).first()
    user_balance = User.get_ktd_balance(current_user.id)
    transaction_hash, is_error = token_utils.take_TKD(user_balance, user.private_key)
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
    log('Удаление пользователя с id {}'.format(uid))
    return redirect('users_list')


@app.route('/delete_team', methods=['GET'])
@login_required
def delete_team():
    if not User.check_admin(current_user.id):
        log('Попытка удаления команды (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))
    tid = request.args.get('tid')
    TeamRoles.query.filter_by(team_id=tid).delete()
    Membership.query.filter_by(team_id=tid).delete()
    Teams.query.filter_by(id=tid).delete()
    db.session.commit()
    log('Удаление команды с id {}'.format(tid))
    return redirect('/teams_crew')


@app.route('/red_team', methods=['GET', 'POST'])
@login_required
def red_team():
    if not User.check_admin(current_user.id):
        log('Попытка удаления команды (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))
    form = RedTeamForm()
    tid = request.args.get('tid')
    team = Teams.query.get(tid)
    statuses = [(1, 'Оценивается'), (2, 'Не оценивается'), (3, 'Состояние не определено'),
                (4, 'Участвует в еженедельной оценке'), (5, 'Заморожен')]
    if form.validate_on_submit():
        team.name = form.title.data
        team.type = form.status.data
        db.session.commit()
    return render_template('red_team.html', title='Редактирование команды', team=team,
                           access=get_access(current_user), form=form, statuses=statuses)


@app.route('/teams_crew', methods=['POST', 'GET'])
@login_required
def teams_crew():
    # if not (User.check_admin(current_user.id) or TeamRoles.check_team_lead(current_user.id)):
    #     log('Попытка просмотра страницы с составами команд (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            access=get_access(current_user))
    log('Просмотр страницы с составами команд')
    form = TeamAdding()
    if form.validate_on_submit():
        team = Teams(name=form.title.data, type=int(form.type.data))
        db.session.add(team)
        db.session.commit()
        log('Добавление команды с названием "{}"'.format(form.title.data))
        return redirect('/teams_crew?s=1')
    teams = Teams.query.all()
    info = list()
    for team in teams:
        members = Membership.get_crew_of_team(team.id)
        members_list = []
        for m in members:
            members_list.append([m[0], m[1], m[2], TeamRoles.check_team_lead(m[0], team.id)])
        if User.check_admin(current_user.id):
            info.append((team, members_list, True))
        else:
            info.append(
                (team, members_list, TeamRoles.check_team_lead(current_user.id, team.id)))
    s = 's' in request.args and request.args.get('s') == '1'
    return render_template('teams_crew.html', title='Текущие составы команд', info=info,
                           access=get_access(current_user), form=form, scroll=s)


@app.route('/edit_team', methods=['GET', 'POST'])
@login_required
def edit_team():
    # if not (User.check_admin(current_user.id) or TeamRoles.check_team_lead(current_user.id,
    #                                                                        int(request.args.get('tid')))):
    #     log('Попытка просмотра страницы с редактированием команды (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            access=get_access(current_user))
    tid = int(request.args.get('tid'))
    log('Просмотр страницы с редактированием команды с id {}'.format(tid))
    form = MemberAdding()
    if form.validate_on_submit():
        new_member_id = int(form.name.data)
        if new_member_id > 0:
            new_member = Membership(user_id=new_member_id, team_id=tid)
            db.session.add(new_member)
            db.session.commit()
            log('Добавление пользователя с id {} в команду с id {}'.format(new_member_id, tid))
        return redirect(url_for('edit_team', tid=tid))
    title = Teams.query.filter_by(id=tid).first().name
    members = Membership.get_crew_of_team(tid)
    users = User.query.order_by(User.name).all()
    for team_member in members:
        if team_member[0] in [user.id for user in users]:
            for user in users:
                if user.id == team_member[0]:
                    users.remove(user)

    return render_template('edit_team.html', title='Редактировать состав команды',
                           team_title=title, members=members, tid=tid, form=form, users=users,
                           access=get_access(current_user),
                           can_edit=current_user.is_admin or TeamRoles.check_team_lead(current_user.id, tid))


@app.route('/delete_member', methods=['GET'])
@login_required
def delete_member():
    if not (User.check_admin(current_user.id) or TeamRoles.check_team_lead(current_user.id,
                                                                           int(request.args.get('tid')))):
        log('Попытка удаления пользователя из команды (ГВ)')
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    tid = request.args.get('tid')
    uid = request.args.get('uid')
    Membership.query.filter_by(team_id=tid, user_id=uid).delete()
    TeamRoles.query.filter_by(team_id=tid, user_id=uid).delete()
    db.session.commit()
    log('Удаление пользователя с id {} из команды с id {}'.format(uid, tid))
    return redirect('edit_team?tid=' + str(tid))


@app.route('/assessment_page')
@login_required
def assessment_page():
    flag = QuestionnaireTable.is_opened()
    return render_template('assessment_page.html', title='Оценка вклада', flag=flag)


@app.route('/blockchain')
@login_required
def blockchain():
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    eth_exchange_rate = exchange_rate_record.exchange_rate if exchange_rate_record else 248000
    ktd_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
    ktd_price = User.get_ktd_price(current_user.id) * eth_exchange_rate
    kti_price = User.get_kti_price(current_user.id) * eth_exchange_rate
    eth_balance = User.get_eth_balance(current_user.id)

    kti_total = token_utils.get_main_contract_KTI_balance() / KT_BITS_IN_KT

    return render_template('blockchain.html', title='Блокчейн', ktd_balance=ktd_balance,
                           ktd_price=ktd_price, kti_total=kti_total, kti_price=kti_price,
                           eth_balance=eth_balance, contract_address=contract_address)


@app.route('/change_to_eth', methods=['GET', 'POST'])
@login_required
def change_to_eth():
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    eth_exchange_rate = exchange_rate_record.exchange_rate if exchange_rate_record else 248000
    ktd_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
    ktd_eth_price = User.get_ktd_price(current_user.id)
    limit = User.get_KTD_seller_limit(current_user.id) / KT_BITS_IN_KT
    ktd_price = ktd_eth_price * eth_exchange_rate
    user = User.query.filter_by(id=current_user.id).first()
    has_access_to_sell = User.has_access_to_sell(user.id)
    form = ChangeToEthForm()

    if form.validate_on_submit():
        if ktd_balance < float(form.amount.data.replace(' ', '')):
            flash('Недостаточно токенов.', 'error')
            return redirect('change_to_eth')
        if limit < float(form.amount.data.replace(' ', '')):
            flash('Превышен лимит продажи токенов.', 'error')
            return redirect('change_to_eth')
        transaction = Transaction(type='Продажа токена', summa=float(form.amount.data.replace(' ', '')),
                                  receiver=User.get_full_name(user.id), date=datetime.datetime.now(),
                                  status='Успешно')
        message, is_error = token_utils.sell_KTD(int(float(form.amount.data.replace(' ', '')) * KT_BITS_IN_KT),
                                                 user.private_key)

        if is_error:
            transaction.status = 'Ошибка'
            db.session.add(transaction)
            db.session.commit()
            flash(message, 'error')
            return redirect(url_for('change_to_eth'))
        db.session.add(transaction)
        db.session.commit()
        flash(message, 'success')
    return render_template('change_to_eth.html', title='Обменять на eth',
                           ktd_balance=ktd_balance, ktd_price=ktd_price, form=form,
                           has_access_to_sell=has_access_to_sell, ktd_eth_price=ktd_eth_price,
                           limit=limit)


@app.route('/change_address', methods=['GET', 'POST'])
@login_required
def change_address():
    form = ChangeAddress()

    user = User.query.filter_by(id=current_user.id).first()

    current_address = user.get_eth_address(current_user_id=current_user.id)

    if form.validate_on_submit():
        user.private_key = form.new_private_key.data
        db.session.commit()

        return redirect(url_for('change_address'))

    return render_template('change_address.html', title='Изменить адрес кошелька', form=form,
                           current_address=current_address)


@app.route('/transfer_ktd', methods=['GET', 'POST'])
@login_required
def transfer_ktd():
    ktd_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
    user = User.query.filter_by(id=current_user.id).first()
    form = TransferKtdForm()
    if form.validate_on_submit():
        transaction = Transaction(type='Перевод токенов', summa=float(form.num.data.replace(' ', '')),
                                  receiver=User.get_full_name(user.id), date=datetime.datetime.now(),
                                  status='Успешно')
        num = int(float(form.num.data) * KT_BITS_IN_KT)
        address = form.address.data
        message, is_error = token_utils.transfer_KTD(num, address, user.private_key)
        if is_error:
            flash(message, 'error')
        else:
            flash(message, 'success')
        if is_error:
            transaction.status = 'Ошибка'
            db.session.add(transaction)
            db.session.commit()

            return redirect(url_for('transfer_ktd'))
        db.session.add(transaction)
        db.session.commit()

    return render_template('transfer_ktd.html', title='Перевести токены вклада', form=form,
                           ktd_balance=ktd_balance)


@app.route('/manage_ktd', methods=['GET', 'POST'])
@login_required
def manage_ktd():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    contract_balance = w3.eth.getBalance(Web3.toChecksumAddress(contract_address)) / ETH_IN_WEI
    ktd_total = token_utils.get_main_contract_KTD_balance() / KT_BITS_IN_KT

    form = ManageKTIForm()

    if form.validate_on_submit():
        address = form.address.data
        num = int(float(form.num.data.replace(' ', '')) * KT_BITS_IN_KT)
        message, is_error = token_utils.set_KTD_seller(address, num, os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
        if is_error:
            flash(message, 'error')
        else:
            flash(message, 'success')
        return redirect(url_for('manage_ktd'))
    return render_template('manage_ktd.html', title='Доступ к токенам вклада',
                           contract_balance=contract_balance, ktd_total=ktd_total, form=form)


@app.route('/manage_kti', methods=['GET', 'POST'])
@login_required
def manage_kti():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    contract_balance = w3.eth.getBalance(Web3.toChecksumAddress(contract_address)) / ETH_IN_WEI
    kti_total = token_utils.get_main_contract_KTI_balance() / KT_BITS_IN_KT

    form = ManageKTIForm()

    if form.validate_on_submit():
        address = form.address.data
        num = int(float(form.num.data.replace(' ', '')) * KT_BITS_IN_KT)
        message, is_error = token_utils.set_KTI_buyer(address, num, os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
        if is_error:
            flash(message, 'error')
        else:
            flash(message, 'success')

        return redirect(url_for('manage_kti'))

    return render_template('manage_kti.html', title='Доступ к токенам инвестиций',
                           contract_balance=contract_balance, kti_total=kti_total, form=form)


@app.route('/budget')
@login_required
def budget():
    cur_budget = Budget.query.filter_by(is_saved=False).first()
    if cur_budget:
        cur_budget_id = cur_budget.id
    else:
        cur_voting = VotingTable.query.filter(or_(VotingTable.status == 'Active', VotingTable.status == 'Fixed')).first()
        if cur_voting:
            cur_budget = Budget(voting_id=cur_voting.id, who_saved='')
            db.session.add(cur_budget)
            db.session.commit()
            cur_budget_id = cur_budget.id
        else:
            cur_budget_id = 0
    return render_template('budget.html', title='Бюджет', cur_budget_id=cur_budget_id)


@app.route('/all_budget_records/')
def all_budget_records():
    data = Budget.query.filter_by(is_saved=True).all()
    for row in data:
        voting = VotingTable.query.get(row.voting_id)
        row.voting = f'{voting.month_from} - {voting.month_to}'
        records = BudgetRecord.query.filter_by(budget_id=row.id).all()
        row.summ = sum([roww.summa for roww in records])
    return render_template('all_budget_records.html', data=data)


@app.route('/current_budget/<budget_id>')
def current_budget(budget_id):
    budget_id = int(budget_id)
    if budget_id == 0:
        return render_template('current_budget.html', data=[], flag=True)
    data = BudgetRecord.query.filter_by(budget_id=budget_id).all()
    voting = VotingTable.query.get(Budget.query.get(budget_id).voting_id)
    not_saved = Budget.query.get(budget_id).is_saved == False
    return render_template('current_budget.html', data=data, not_saved=not_saved, budget_id=budget_id, voting=voting)


@app.route('/token_exchange_rate_by_default', methods=['POST'])
@login_required
def token_exchange_rate_by_default():
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000
    start_price = (1 / exchange_rate) * ETH_IN_WEI
    start_month = 12 * 2017 + 5
    current_month = datetime.datetime.now().year * 12 + datetime.datetime.now().month
    n = current_month - start_month
    price = int(start_price * math.pow(1.05, n - 1))
    private_key = os.environ.get(
        'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
    ktd_message, is_ktd_error = token_utils.set_KTD_price(price, private_key)
    kti_message, is_kti_error = token_utils.set_KTI_price(price, private_key)
    if (not is_ktd_error) and (not is_kti_error):
        token_exchange_rate = TokenExchangeRate(date=datetime.datetime.now(), exchange_rate_in_wei=price,
                                                is_default_calculation_method=True)
        db.session.add(token_exchange_rate)
        db.session.commit()

    return redirect('/emission')


@app.route('/token_exchange_rate_by_profit', methods=['POST'])
@login_required
def token_exchange_rate_by_profit():
    current_profit = db.session.query(func.sum(Profit.summa)).first()[0] or 0
    current_ktd_price = User.get_ktd_price(current_user.id)
    ktd_total = token_utils.get_KTD_total(ktd_address)
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000

    new_ktd_price = (current_profit / (ktd_total / KT_BITS_IN_KT)) / exchange_rate

    print(new_ktd_price, current_ktd_price)

    if new_ktd_price > current_ktd_price:
        print(token_utils.set_KTD_price(int(new_ktd_price * ETH_IN_WEI), os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'))
        token_utils.set_KTI_price(int(new_ktd_price * ETH_IN_WEI), os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
    return redirect('/emission')


@app.route('/change_token_exchange_rate', methods=['GET', 'POST'])
@login_required
def change_token_exchange_rate():
    if not current_user.is_accountant:
        return redirect(url_for('home'))

    eth_exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    if eth_exchange_rate_record:
        eth_exchange_rate = eth_exchange_rate_record.exchange_rate
    else:
        eth_exchange_rate = 248000

    token_exchange_rate_in_rub = User.get_kti_price(current_user.id) * eth_exchange_rate

    form = ChangeEthExchangeRate()

    if form.validate_on_submit():
        price = (float(form.price.data.replace(' ', '')) / eth_exchange_rate) * ETH_IN_WEI

        private_key = os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
        ktd_message, is_ktd_error = token_utils.set_KTD_price(int(price), private_key)
        kti_message, is_kti_error = token_utils.set_KTI_price(int(price), private_key)
        if (not is_ktd_error) and (not is_kti_error):
            token_exchange_rate = TokenExchangeRate(date=datetime.datetime.now(), exchange_rate_in_wei=price,
                                                    is_default_calculation_method=False)
            db.session.add(token_exchange_rate)
            db.session.commit()

        return redirect(url_for('emission'))

    return render_template('change_token_exchange_rate.html', title='Изменить курс токенов', form=form,
                           exchange_rate=token_exchange_rate_in_rub)


@app.route('/change_eth_exchange_rate', methods=['GET', 'POST'])
@login_required
def change_eth_exchange_rate():
    if not current_user.is_accountant:
        return redirect(url_for('home'))

    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000

    form = ChangeEthExchangeRate()

    if form.validate_on_submit():
        price = float(form.price.data.replace(' ', ''))
        eth_exchange_rate = EthExchangeRate(date=datetime.datetime.now(), exchange_rate=price)

        db.session.add(eth_exchange_rate)
        db.session.commit()

        return redirect(url_for('emission'))

    return render_template('change_eth_exchange_rate.html', title='Изменить курс eth', form=form,
                           exchange_rate=exchange_rate)


@app.route('/fix_profit', methods=['GET', 'POST'])
@login_required
def fix_profit():
    if not current_user.is_accountant:
        return redirect(url_for('home'))

    form = FixProfit()

    if form.validate_on_submit():
        profit = float(form.profit.data.replace(' ', ''))
        profit_record = Profit(date=datetime.datetime.now(), summa=profit)

        db.session.add(profit_record)
        db.session.commit()

        # return redirect(url_for('emission'))
        return redirect('/profit_records')

    return render_template('fix_profit.html', title='Зафиксировать прибыль', form=form)


@app.route('/confirm_emission')
@login_required
def confirm_emission():
    if not current_user.is_accountant:
        return redirect(url_for('home'))

    return render_template('confirm_emission.html', title='Произвести эмиссию')


@app.route('/make_emission')
@login_required
def make_emission():
    if not current_user.is_accountant:
        return redirect(url_for('home'))
    kti_price = User.get_kti_price(current_user.id)
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_month_last_day = (
                datetime.date(current_year + int(current_month / 12), current_month % 12 + 1, 1) - datetime.timedelta(
            days=1)).day
    current_budget = db.session. \
                         query(func.sum(BudgetRecord.summa)). \
                         filter(
        BudgetRecord.date >= datetime.datetime(
            current_year,
            current_month,
            1
        )
    ). \
                         filter(
        BudgetRecord.date <= datetime.datetime(
            current_year,
            current_month,
            current_month_last_day
        )
    ).first()[0] or 0
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000

    kti_emission = int(((current_budget / exchange_rate) / kti_price) * KT_BITS_IN_KT)
    ktd_emission = int((kti_emission * 3 / 7) * KT_BITS_IN_KT)

    contract_checksum_address = Web3.toChecksumAddress(contract_address)

    token_utils.mint_KTI(kti_emission, contract_checksum_address, os.environ.get(
        'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
    VotingTable.query.get(VotingTable.current_emission_voting_id()).status = 'Distribution'
    db.session.commit()
    return redirect(url_for('emission'))


@app.route('/emission')
@login_required
def emission():
    ktd_price = User.get_ktd_price(current_user.id)
    kti_price = User.get_kti_price(current_user.id)
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_month_last_day = (
                datetime.date(current_year + int(current_month / 12), current_month % 12 + 1, 1) - datetime.timedelta(
            days=1)).day
    current_budget = db.session. \
                         query(func.sum(BudgetRecord.summa)). \
                         filter(
        BudgetRecord.date >= datetime.datetime(
            current_year,
            current_month,
            1
        )
    ). \
                         filter(
        BudgetRecord.date <= datetime.datetime(
            current_year,
            current_month,
            current_month_last_day
        )
    ).first()[0] or 0
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000

    kti_emission = (current_budget / exchange_rate) / kti_price
    ktd_emission = kti_emission * 3 / 7

    voting_id = VotingTable.current_emission_voting_id()
    try:
        # voting_id = VotingTable.query.filter_by(status='Finished').all()[-1].id
        users = [(user.id, user.name + ' ' + user.surname) for user in User.query.all() if
                 User.check_can_be_marked(user.id)]
        marks_counter = 0
        for user in users:
            res = [user[1]]
            user_res = db.session.query(func.avg(VotingInfo.mark)).outerjoin(Voting,
                                                                             Voting.id == VotingInfo.voting_id).filter(
                Voting.voting_id == voting_id, VotingInfo.cadet_id == user[0]).group_by(
                VotingInfo.criterion_id).all()
            for mark in user_res:
                if float(mark[0]) == 1.0:
                    marks_counter += 1
    except Exception as e:
        marks_counter = -1
        users = []
    # voting_id = VotingTable.current_fixed_voting_id()
    distribution_id = VotingTable.current_distribution_voting_id()
    return render_template('emission.html', title='Эмиссия токенов', ktd_price=ktd_price,
                           kti_price=kti_price, current_budget=current_budget, exchange_rate=exchange_rate,
                           kti_emission=kti_emission, ktd_emission=ktd_emission, voting_id=voting_id,
                           amount_of_assesment_members=len(users), total_score=marks_counter,
                           distribution_id=distribution_id)


@app.route('/confirm_tokens_distribution')
@login_required
def confirm_tokens_distribution():
    if not current_user.is_accountant:
        return redirect(url_for('home'))

    return render_template('confirm_tokens_distribution.html', title='Распределить токены')


@app.route('/make_tokens_distribution')
@login_required
def make_tokens_distribution():
    if not current_user.is_accountant:
        return redirect(url_for('home'))
    kti_price = User.get_kti_price(current_user.id)
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_month_last_day = (
                datetime.date(current_year + int(current_month / 12), current_month % 12 + 1, 1) - datetime.timedelta(
            days=1)).day
    current_budget = db.session. \
                         query(func.sum(BudgetRecord.summa)). \
                         filter(
        BudgetRecord.date >= datetime.datetime(
            current_year,
            current_month,
            1
        )
    ). \
                         filter(
        BudgetRecord.date <= datetime.datetime(
            current_year,
            current_month,
            current_month_last_day
        )
    ).first()[0] or 0
    exchange_rate_record = EthExchangeRate.query.order_by(EthExchangeRate.date.desc()).first()
    exchange_rate = 0

    if (exchange_rate_record):
        exchange_rate = exchange_rate_record.exchange_rate
    else:
        exchange_rate = 248000

    kti_emission = (current_budget / exchange_rate) / kti_price
    ktd_emission = kti_emission * 3 / 7

    cur_voting = VotingTable.query.filter_by(status='Distribution').first()
    if cur_voting:
        voting_id = cur_voting.id
    else:
        voting_id = VotingTable.query.filter_by(status='Finished').all()[-1].id
    criterions = [c.name for c in Criterion.query.all()]
    users = [(user.id, user.name + ' ' + user.surname, User.get_eth_address(user.id)) for user in User.query.all() if
             User.check_can_be_marked(user.id)]
    marks_counter = 0
    for user in users:
        res = [user[1]]
        user_res = db.session.query(func.avg(VotingInfo.mark)).outerjoin(Voting,
                                                                         Voting.id == VotingInfo.voting_id).filter(
            Voting.voting_id == voting_id, VotingInfo.cadet_id == user[0]).group_by(
            VotingInfo.criterion_id).all()
        for mark in user_res:
            if float(mark[0]) == 1.0:
                marks_counter += 1
    ktd_in_mark = ktd_emission / marks_counter if marks_counter >= 0 else 0
    for user in users:
        res = [user[1]]
        user_res = db.session.query(func.avg(VotingInfo.mark)).outerjoin(Voting,
                                                                         Voting.id == VotingInfo.voting_id).filter(
            Voting.voting_id == voting_id, VotingInfo.cadet_id == user[0]).group_by(
            VotingInfo.criterion_id).all()
        marks = sum([int(current_res[0]) for current_res in user_res])
        mint_amount = int((ktd_in_mark * marks) * KT_BITS_IN_KT)
        token_utils.mint_KTD(mint_amount, user[2], os.environ.get(
            'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
    VotingTable.query.filter_by(status='Distribution').first().status = 'Finished'
    db.session.commit()
    return redirect(url_for('emission'))


@app.route('/services')
@login_required
def services():
    return render_template('services.html', title='Услуги', services=KorpusServices.query.all())


@app.route('/change_service/<service_id>', methods=['GET', 'POST'])
@login_required
def change_service(service_id):
    service = KorpusServices.query.get(service_id)
    form = AddServiceForm()
    if form.validate_on_submit():
        service.name = form.name.data
        service.price = form.price.data.replace(' ', '')
        service.unit = form.unit.data.lower()
        service.address = form.address.data
        service.description = form.description.data
        db.session.commit()
        return redirect('/services')
    return render_template('change_service.html', title='Изменить услугу', service=service, form=form)


@app.route('/service/<service_id>', methods=['GET', 'POST'])
@login_required
def service_info(service_id):
    service = KorpusServices.query.get(service_id)
    form = PrePayServiceForm()
    if form.validate_on_submit():
        user_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
        form2 = ConfirmForm()
        if form2.validate_on_submit() and form2.stub.data:
            print(float(form2.stub.data))
            return render_template('service_pay_confirmation.html', title='Подтверждение операции',
                                   price=float(form2.stub.data), service=service)
        return render_template('service_pay.html', title=service.name, service=service,
                               price=int(form.amount.data) * service.price, user_balance=user_balance, form=form2)
    return render_template('service_info.html', title=service.name, service=service, form=form)


@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    form = AddServiceForm()
    if form.validate_on_submit():
        service = KorpusServices(name=form.name.data, price=form.price.data.replace(' ',''),
                                 unit=form.unit.data.lower(),address=form.address.data,
                                 description=form.description.data)
        db.session.add(service)
        db.session.commit()
        return redirect('/services')
    return render_template('add_service.html', title='Добавить услугу', form=form)


@app.route('/house_rent', methods=['GET'])
@login_required
def house_rent():
    house_rent_record = KorpusServices.query.filter_by(name='HouseRent').first()
    house_rent_price = house_rent_record.price if house_rent_record else 0
    user_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT

    return render_template('house_rent.html', title='Аренда дома Корпус', house_rent_price=house_rent_price,
                           user_balance=user_balance)


@app.route('/house_rent_confirmation', methods=['GET'])
@login_required
def house_rent_confirmation():
    house_rent_record = KorpusServices.query.filter_by(name='HouseRent').first()
    house_rent_price = house_rent_record.price if house_rent_record else 0

    return render_template('house_rent_confirmation.html', title='Подтверждение операции',
                           house_rent_price=house_rent_price)


@app.route('/confirm_pay')
@login_required
def confirm_pay():
    s_id = int(request.args.get('s_id'))
    service = KorpusServices.query.get(s_id)
    price = float(request.args.get('price'))

    # Оплата услуги через блокчейн
    user_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
    user = User.query.filter_by(id=current_user.id).first()
    user_address = user.get_eth_address(current_user_id=current_user.id)
    if user_balance < price:
        return redirect(f'/service/{s_id}')
    result, is_error = token_utils.make_payment(user_address, int(price * KT_BITS_IN_KT), user.private_key)
    if is_error:
        print(result)
        return redirect(f'/service/{s_id}')
    # На выходе - промокод
    payments = ServicePayments.query.all()
    code = result #f'{len(payments) + 1}'
    payment = ServicePayments(service_id=s_id, user_id=current_user.id, paid_amount=price / service.price, active=True,
                              code=code, date=datetime.datetime.now(), transaction_hash='')
    db.session.add(payment)
    db.session.commit()
    requests.post('https://bot.eos.korpus.io/promocode', data={'user_id': current_user.id, 'code': code})
    return redirect('/services')


@app.route('/check_code', methods=['GET', 'POST'])
@login_required
def check_code():
    form = CheckCodeForm()
    form2 = CheckCodeForm2()
    if form.submit.data and form.validate_on_submit():
        code = form.code.data
        payment = ServicePayments.query.filter_by(code=code).first()
        if payment:
            user = User.query.get(payment.user_id)
            service = KorpusServices.query.get(payment.service_id)
            status = 'Активен' if payment.active else 'Использован'
            info = {'user': f'{user.name} {user.surname}', 'service': service.name, 'unit': service.unit,
                    'paid_amount': payment.paid_amount, 'date': payment.date, 'status': status,
                    'active': payment.active, 'code': code}
            return render_template('check_code.html', title='Проверить код', form2=form2, info=info)
        else:
            return render_template('check_code.html', title='Проверить код', form=form, message='Промокод не найден')
    if form2.submit2.data and form2.validate_on_submit():
        code = form2.code2.data
        payment = ServicePayments.query.filter_by(code=code).first()
        payment.active = False
        db.session.commit()
        return render_template('check_code.html', title='Проверить код', form=form, message='Промокод активирован')
    return render_template('check_code.html', title='Проверить код', form=form)


@app.route('/confirm_house_rent', methods=['GET'])
@login_required
def confirm_house_rent():
    house_rent_record = KorpusServices.query.filter_by(name='HouseRent').first()
    house_rent_price = house_rent_record.price if house_rent_record else 0
    user_balance = User.get_ktd_balance(current_user.id) / KT_BITS_IN_KT
    user = User.query.filter_by(id=current_user.id).first()

    user_address = user.get_eth_address(current_user_id=current_user.id)

    if user_balance < house_rent_price:
        return redirect('/house_rent')

    result, is_error = token_utils.rent_house(user_address, int(house_rent_price * KT_BITS_IN_KT), os.environ.get(
        'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')

    if is_error:
        print(result)
        return redirect('/house_rent')

    print(result)

    return redirect('/')


@app.route('/add_budget_item/<budget_id>', methods=['GET', 'POST'])
@login_required
def add_budget_item(budget_id):
    form = AddBudgetItemForm()
    budget_id = int(budget_id)
    existing_budget_record = BudgetRecord.query.filter_by(date=datetime.datetime.now().date(),
                                                          item=form.item.data).first()
    #votings = VotingTable.query.filter_by(status='Fixed').all()
    if form.validate_on_submit():
        summa = round(float(form.cost.data.replace(' ', '')), 2)
        who_added = f'{User.get_full_name(current_user.id)}'
        #voting_id = int(form.voting.data)
        bud_date = datetime.datetime.now().date()
        # if voting_id == 0:
        #     bud_date = datetime.datetime.now().date()
        # else:
        #     month = VotingTable.query.get(voting_id).month_from
        #     month, year = month.split(' ')
        #     year = int(year[:4])
        #     month = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь',
        #                     'октябрь', 'ноябрь', 'декабрь'].index(month) + 1
        #     bud_date = datetime.datetime(year=year, month=month, day=20, hour=12, minute=0, second=0, microsecond=0)
        record = BudgetRecord(date=bud_date, item=form.item.data, summa=summa,
                              who_added=who_added, budget_id=budget_id)
        if existing_budget_record:
            existing_budget_record.summa = summa
            existing_budget_record.who_added = who_added
            db.session.commit()

            return redirect(f'/current_budget/{budget_id}')
        db.session.add(record)
        db.session.commit()
        return redirect(f'/current_budget/{budget_id}')
    return render_template('add_budget_item.html', title='Добавить статью', form=form, budget_id=budget_id)


@app.route('/write_to_blockchain/<budget_id>')
@login_required
def write_to_blockchain(budget_id):
    return render_template('write_to_blockchain.html', title='Записать в блокчейн', budget_id=budget_id)


@app.route('/save_to_blockchain/<budget_id>')
@login_required
def save_to_blockchain(budget_id):
    budget_id = int(budget_id)
    if not current_user.is_admin:
        return redirect(url_for('home'))

    account = w3.eth.account.privateKeyToAccount(
        os.environ.get('ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')

    budget_records = BudgetRecord.query.filter_by(budget_id=budget_id).all()

    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    for budget_record in budget_records:
        date = budget_record.date
        timestamp = datetime.datetime(year=date.year, month=date.month,
                                      day=date.day).timestamp()
        budget_item = budget_record.item
        cost = round(budget_record.summa, 2) * 100

        nonce = w3.eth.getTransactionCount(account.address, 'pending')

        estimateGas = KorpusContract.functions.setBudget(int(timestamp), budget_item, int(cost)).estimateGas({
            'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('11', 'gwei'),
            'chainId': 3
        })
        transaction = KorpusContract.functions.setBudget(int(timestamp), budget_item, int(cost)).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': estimateGas,
                'gasPrice': w3.toWei('29', 'gwei'),
                'chainId': 3
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)

        try:
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            transaction_hash = txn_hash.hex()

            #budget_record.is_saved = True
        except Exception as err:
            print(err)
    Budget.query.get(budget_id).is_saved = True
    Budget.query.get(budget_id).who_saved = f'{User.get_full_name(current_user.id)}'
    db.session.commit()

    return redirect(url_for('budget'))


@app.route('/add_to_blockchain')
@login_required
def add_to_blockchain():
    return render_template('add_to_blockchain.html', title='Записать в блокчейн')


@app.route('/write_voting_progress')
@login_required
def write_voting_progress():
    cur_id = VotingTable.current_fixed_voting_id()
    voting_info = VotingInfo.query.filter_by(voting_id=cur_id).all()
    users_info = [(User.query.filter_by(id=info.cadet_id).first(),
                   Membership.query.filter_by(user_id=info.cadet_id).first(),
                   info,
                   Axis.query.filter_by(id=info.criterion_id).first()) for info in voting_info]
    for user_data in users_info:
        team = Teams.query.filter_by(id=user_data[1].team_id).first()
        cur_date = datetime.datetime.now()
        date = int(str(cur_date.year) + str(cur_date.month) + str(cur_date.day))
        token_utils.save_voting_to_blockchain(team=team.name, student=User.get_full_name(user_data[0].id),
                                              date=date,
                                              axis=user_data[3].name,
                                              points=user_data[2].mark,
                                              private_key=os.environ.get(
                                                  'ADMIN_PRIVATE_KEY') or '56bc1794425c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66')
    VotingTable.query.get(cur_id).status = 'Emission'
    db.session.commit()
    return redirect('/questionnaire_progress')


@app.route('/delete_budget_row/<budget_id>', methods=['POST'])
@login_required
def delete_budget_row(budget_id):
    row_id = int(request.form.get('id'))
    BudgetRecord.query.filter_by(id=row_id).delete()
    db.session.commit()
    return redirect(f'/current_budget/{budget_id}')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.tg_nickname = form.tg_nickname.data
        current_user.birthday = form.birthday.data
        current_user.education = form.education.data
        current_user.work_exp = form.work_exp.data
        current_user.vk_url = form.vk_url.data
        current_user.fb_url = form.fb_url.data
        current_user.inst_url = form.inst_url.data
        current_user.courses = form.courses.data
        db.session.commit()
    return render_template('profile.html', title='Профиль', form=form, script='signup.js', profile=True)


@app.route('/community')
@login_required
def community():
    teams = Membership.query.filter_by(user_id=current_user.id).all()
    return render_template('community.html', title='Сообщество', team_id=teams[0].team_id if teams else None)


@app.route('/participate')
@login_required
def participate():
    if QuestionnaireTable.is_opened() and User.check_can_be_marked(current_user.id):
        return render_template('participate.html', title='Участвовать в оценке')
    else:
        return redirect('/assessment')


@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    # if not (User.check_tracker(current_user.id) or User.check_top_cadet(current_user.id)
    #         or User.check_expert(current_user.id) or User.check_chieftain(current_user.id)
    #         or User.check_teamlead(current_user.id)):
    #     log('Попытка просмотра страницы с оценкой (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
    #                            access=get_access(current_user))

    log('Просмотр страницы с оценкой')
    if QuestionnaireTable.is_opened() and User.check_can_be_marked(current_user.id):
        return redirect('/questionnaire_position')
        # return redirect('/questionnaire_self')
    if not VotingTable.is_opened():
        return render_template('voting_progress.html', title='Оценка', access=get_access(current_user))
    if (User.check_expert(current_user.id) + User.check_top_cadet(current_user.id)
        + User.check_tracker(current_user.id) + User.check_chieftain(current_user.id) + User.check_teamlead(
                current_user.id)) == 0:
        return render_template('voting_self_progress.html', title='Оценка', access=get_access(current_user),
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
            return render_template('assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        return redirect(url_for('assessment_team', axis_id=2))

    if User.check_top_cadet(current_user.id):  # and Axis.is_available(1):
        teams_for_voting = len(Teams.get_teams_for_voting())
        if len(Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 1,
                                   Voting.voting_id == VotingTable.current_voting_id()).all()) >= teams_for_voting:
            return render_template('assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        return redirect(url_for('assessment_team', axis_id=1))

    if User.check_chieftain(current_user.id):  # and Axis.is_available(3):
        if Voting.query.filter(Voting.user_id == current_user.id, Voting.axis_id == 3,
                               Voting.voting_id == VotingTable.current_voting_id()).first():
            return render_template('assessment_axis.html', title='Выбор оси', is_first=False,
                                   access=get_access(current_user), axises=[], is_third=False,
                                   is_second=False)
        else:
            return redirect(url_for('c', axis_id=3, team_id=0))

    return render_template('assessment.html', title='Оценка',
                           access=get_access(current_user))


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
    # teams = [(team.id, team.name) for team in Teams.query.filter_by(type=1) if
    #          Voting.check_on_assessment(current_user.id, team.id, 1)]
    # is_first = True if len(teams) else False
    # teams = [(team.id, team.name) for team in Teams.query.filter_by(type=1) if
    #          Voting.check_on_assessment(current_user.id, team.id, 2)]
    # is_second = True if len(teams) else False
    # is_third = True
    # if not Voting.check_on_assessment(current_user.id, 0, 3):
    #     is_third = False
    return render_template('assessment_axis.html', title='Оценка', is_first=is_first,
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
    if User.check_tracker(current_user.id) or User.check_expert(current_user.id) or User.check_teamlead(current_user.id):
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
    return render_template('assessment_team.html', title='Выбор команды',
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
        return render_template('authority_voting.html', title='Ось власти', answers=answers,
                               access=get_access(current_user), questions=questions,
                               team_members=cadets, criterions=criterions, axis=axis, team_id=team_id, is_first=is_first,
                           is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                           voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus, voting_num_auth=voting_num_auth)
    elif axis_id == '2':
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if User.check_cadet(member.user_id)]
        # if current_user.id != member.user_id and User.check_cadet(member.user_id)]
        team = Teams.query.filter_by(id=team_id).first().name
        #current_month = datetime.datetime.now().month
        monthes = [5, 6, 7, 8, 9]
        dates = []
        for current_month in monthes:
            dates += db.session.query(WeeklyVoting.date).filter(func.month(WeeklyVoting.date) == current_month,
                                                           WeeklyVoting.team_id == team_id,
                                                           WeeklyVoting.finished == 1).distinct().all()
        voting_results = []
        voting_dict = {}
        for user in team_members:
            voting_dict[user[0]] = {'name': f'{user[1]} {user[2]}', 'marks1': [], 'marks2': [], 'marks3': []}
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
        return render_template('business_voting.html', title='Ось дела',
                               access=get_access(current_user), team_id=team_id, voting_results=voting_results,
                               dates=dates_str,
                               team_members=team_members, axis=axis, criterions=criterions, team_title=team,
                               voting_dict=voting_dict, is_first=is_first,
                           is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting,
                           voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus, voting_num_auth=voting_num_auth)
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
        return render_template('relations_voting.html', title='Ось отношений', answers=answers, images=images,
                               access=get_access(current_user), team_id=team_id,  # q_ids=q_ids,
                               team_members=team_members, axis=axis, criterions=criterions, team_title=team, is_first=is_first,
                           is_third=is_third, is_second=is_second, teams_for_voting=teams_for_voting, is_last=is_last,
                           voting_num_rel=voting_num_rel, voting_num_bus=voting_num_bus, voting_num_auth=voting_num_auth)


@app.route('/get_members_of_team', methods=['GET', 'POST'])
def get_members_of_team():
    team_id = int(request.args.get('team_id'))
    log('Получение списка пользователей команды с id {}'.format(team_id))
    if team_id == 0:
        team_members = [(user.id,
                         User.query.filter_by(id=user.id).first().name,
                         User.query.filter_by(id=user.id).first().surname)
                        for user in User.query.all() if
                        User.check_can_be_marked(user.id) and current_user.id != user.id]
    else:
        team_members = [(member.user_id,
                         User.query.filter_by(id=member.user_id).first().name,
                         User.query.filter_by(id=member.user_id).first().surname)
                        for member in Membership.query.filter_by(team_id=team_id)
                        if current_user.id != member.user_id and User.check_cadet(member.user_id)]
    return jsonify({'members': team_members})


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
    return render_template('voting_summary.html', voting_info=voting_info, is_first=is_first,
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
    return render_template('assessment_error.html', title='Лимит исчерпан',
                           access=get_access(current_user))


@app.route('/voting_progress', methods=['GET', 'POST'])
@login_required
def voting_progress():
    # if not User.check_admin(current_user.id):
    #     log('Попытка просмотра страницы с прогрессом оценки (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
    #                            access=get_access(current_user))

    log('Просмотр страницы с прогрессом оценки')
    is_opened = QuestionnaireTable.is_opened()
    if is_opened:
        counter, questionnaire, not_participated_team_info, not_participated_self_info = get_questionnaire_progress()
        return render_template('voting_progress.html', title='Прогресс голосования',
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

        # if Axis.is_available(1):
        #     rel_text = 'Запретить голосование по оси отношений'
        # else:
        #     rel_text = 'Открыть голосование по оси отношений'
        # if Axis.is_available(2):
        #     bus_text = 'Запретить голосование по оси дела'
        # else:
        #     bus_text = 'Открыть голосование по оси дела'
        # if Axis.is_available(3):
        #     auth_text = 'Запретить голосование по оси власти'
        # else:
        #     auth_text = 'Открыть голосование по оси власти'
        form = StartAssessmentForm()
        if form.validate_on_submit():
            assessment_status = VotingTable(status='Active', month=form.month.data)
            db.session.add(assessment_status)
            db.session.commit()
            log('Открыл оценку')
            return redirect('voting_progress')
        return render_template('voting_progress.html', title='Прогресс голосования',
                               access=get_access(current_user),
                               teams_number=teams_for_voting, relation=relation_results,
                               business=business_results, authority=authority_results, form=form)  # ,
        # rel_text=rel_text, bus_text=bus_text, auth_text=auth_text)
    else:
        form = StartAssessmentForm()
        if form.validate_on_submit():
            if QuestionnaireTable.is_opened():
                return render_template('voting_progress.html', title='Прогресс голосования',
                                       access=get_access(current_user), form=form,
                                       msg='Сначала надо завершить текущий процесс анкетирования')
            assessment_status = VotingTable(status='Active', month=form.month.data)
            db.session.add(assessment_status)
            db.session.commit()
            log('Открыл оценку')
            return redirect('voting_progress')
        return render_template('voting_progress.html', title='Прогресс голосования',
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


@app.route('/manage_statuses', methods=['GET', 'POST'])
@login_required
def manage_statuses():
    if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
        log('Попытка просмотра страницы с редактированием статусов/ролей (ГВ)')
        return render_template('gryazniy_vzlomshik.html', title='Грязный багоюзер',
                               access=get_access(current_user))

    log('Просмотр страницы с редактированием статусов/ролей')
    users = [(user.id, user.surname + ' ' + user.name) for user in User.query.order_by(User.surname).all()]
    return render_template('manage_statuses.html', title='Управление ролями',
                           access=get_access(current_user),
                           users=users)


@app.route('/get_statuses_of_user', methods=['GET'])
def get_statuses_of_user():
    user_id = int(request.args.get('user_id'))
    if user_id == 0:
        statuses = []
        new_statuses = []
    else:
        statuses_id = [s.status_id for s in UserStatuses.query.filter_by(user_id=user_id).all()]
        if User.check_admin(current_user.id):
            all_statuses = [s.id for s in Statuses.query.all()]
        elif User.check_chieftain(current_user.id):
            all_statuses = [s.id for s in Statuses.query.all() if s.id != 1]

        statuses_diff = set(all_statuses).difference(set(statuses_id))
        if len(statuses_diff) > 0:
            new_statuses = [(Statuses.query.filter_by(id=s_id).first().status, s_id) for s_id in statuses_diff]
        else:
            new_statuses = [(Statuses.query.filter_by(id=s_id).first().status, s_id) for s_id in statuses_id]
        statuses = [(Statuses.query.filter_by(id=s_id).first().status, s_id) for s_id in statuses_id]
        log('Просмотр статусов пользователя с id {}'.format(user_id))
    return jsonify({'user_statuses': statuses, 'new_statuses': new_statuses})


@app.route('/get_teams_of_user', methods=['GET'])
def get_teams_of_user():
    user_id = int(request.args.get('user_id'))
    if user_id == 0:
        teams = []
    else:
        teams_id = [m.team_id for m in Membership.query.filter_by(user_id=user_id).all()]
        teams = [(Teams.query.get(t_id).name, t_id) for t_id in teams_id if not Teams.has_teamlead(t_id)]
    return jsonify({'teams': teams})


@app.route('/add_status', methods=['POST'])
def add_status():
    data = request.json
    user_id = int(data['user_id'])
    status_id = int(data['status_id'])
    new_status = UserStatuses(user_id=user_id, status_id=status_id)
    db.session.add(new_status)
    db.session.commit()
    log('Добавление статуса с id {} пользователю с id {}'.format(status_id, user_id))
    return jsonify({'response': 'ok'})


@app.route('/add_teamlead', methods=['POST'])
def add_teamlead():
    data = request.json
    user_id = int(data['user_id'])
    team_id = int(data['team_id'])
    new_status = UserStatuses(user_id=user_id, status_id=4)
    team_role = TeamRoles(user_id=user_id, team_id=team_id, role_id=1)
    db.session.add(team_role)
    db.session.add(new_status)
    db.session.commit()
    # log('Добавление статуса с id {} пользователю с id {}'.format(status_id, user_id))
    return jsonify({'response': 'ok'})


@app.route('/delete_status', methods=['POST'])
def delete_status():
    data = request.json
    user_id = int(data['user_id'])
    status_id = int(data['status_id'])
    UserStatuses.query.filter(UserStatuses.status_id == status_id, UserStatuses.user_id == user_id).delete()
    db.session.commit()
    log('Удаление статуса с id {} пользователю с id {}'.format(status_id, user_id))
    return jsonify({'response': 'ok'})


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
                     as_attachment=True,
                     attachment_filename=filename,
                     mimetype='text/csv')


@app.route('/assessment_results', methods=['GET'])
@login_required
def assessment_results():
    votings = VotingTable.query.all()
    return render_template('assessment_results.html', title='Результаты оценки',
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
        return render_template('assessment_results.html', title='Результаты оценки',
                               access=get_access(current_user),
                               criterions=criterions, info=user_info)
    else:
        return render_template('assessment_results.html', title='Результаты оценки',
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
    return render_template('weekly_results.html', title='Результаты еженедельной оценки',
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
    teams = [t for t in Teams.query.all() if t.type in [1,4]]
    summary_results = []
    for t in teams:
        team_members = [(member.user_id, User.query.filter_by(id=member.user_id).first().name,
                     User.query.filter_by(id=member.user_id).first().surname)
                    for member in Membership.query.filter_by(team_id=t.id) if User.check_cadet(member.user_id)]
        voting_results = []
        date_info = {'date': f'{date.day}.{date.month}.{date.year}'}
        teammates = db.session.query(WeeklyVotingMembers.cadet_id).filter(WeeklyVotingMembers.date == date, WeeklyVotingMembers.team_id == t.id).all()

        if len(teammates) == 0:
            teammates = [user[0] for user in team_members]
        else:
            teammates = [t[0] for t in teammates]
        marks = db.session.query(
                WeeklyVoting.criterion_id,
                WeeklyVoting.user_id,
                func.avg(WeeklyVoting.mark)
            )\
            .filter(WeeklyVoting.date == date, WeeklyVoting.team_id == t.id, WeeklyVoting.finished == 1, WeeklyVoting.user_id.in_(teammates))\
            .group_by(WeeklyVoting.criterion_id, WeeklyVoting.user_id, WeeklyVoting.date)\
            .all()

        mark_res = {teammate: {date: [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0},
                       {'criterion': 'Подтверждение средой', 'mark': 0}]} for teammate in teammates}
        for mark in marks:
            teammate_mark_res = mark_res.get(mark[1])
            if teammate_mark_res is not None:
                criterion = next(criterion for criterion in teammate_mark_res.get(date) if criterion['criterion'] == Criterion.query.get(mark[0]).name)
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
            voting_dict[user[0]] = {'name': f'{user[1]} {user[2]}', 'marks1': [], 'marks2': [], 'marks3': [], 'user_id': user[0]}
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
            mark_res = [{'criterion': 'Движение', 'mark': 0}, {'criterion': 'Завершенность', 'mark': 0}, {'criterion': 'Подтверждение средой', 'mark': 0}]
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


@app.route('/log_page', methods=['GET'])
@login_required
def log_page():
    if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
        return render_template('gryazniy_vzlomshik.html',
                               access=get_access(current_user))

    logs = Log.query.order_by(Log.id.desc()).all()[:100]
    user_logs = [(l.action, User.get_full_name(l.user_id), l.date) for l in logs]
    return render_template('log_page.html', title='Логи', logs=user_logs,
                           access=get_access(current_user))


@app.route('/user_profile', methods=['GET'])
@login_required
def user_profile():
    # if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
    #     log('Попытка просмотра профиля пользователя (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            access=get_access(current_user))
    uid = request.args.get('user_id')
    user = User.query.filter_by(id=uid).first()
    if not user:
        log('Ошибка при просмотре профиля пользователя: пользователь не найден')
        return render_template('user_profile.html', title='Неизвестный пользователь',
                               access=get_access(current_user))
    log('Просмотр профиля пользователя с id {}'.format(uid))
    if user.birthday:
        date = str(user.birthday).split('-')
        date = '{}.{}.{}'.format(date[2], date[1], date[0])
    else:
        date = '-'
    return render_template('user_profile.html', title='Профиль - {} {}'.format(user.surname, user.name),
                           access=get_access(current_user), user=user,
                           date=date)


@app.route('/choose_top_cadets', methods=['GET'])
@login_required
def choose_top_cadets():
    # if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
    #     log('Попытка просмотра страницы с выбором топовых кадетов (ГВ)')
    #     return render_template('gryazniy_vzlomshik.html',
    #                            responsibilities=User.dict_of_responsibilities(current_user.id),
    #                            private_questionnaire=QuestionnaireTable.is_available(1),
    #                            command_questionnaire=QuestionnaireTable.is_available(2),
    #                            user_roles=TeamRoles.dict_of_user_roles(current_user.id),
    #                            team=Membership.team_participation(current_user.id))
    log('Просмотр страницы с выбором топовых кадетов')
    cur_voting = QuestionnaireTable.current_questionnaire_id()
    if TopCadetsVoting.query.filter(TopCadetsVoting.voting_id == cur_voting,
                                    TopCadetsVoting.voter_id == current_user.id).first():
        return render_template('top_cadets_error.html', title='Выбор оценивающих по оси отношений',
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

    return render_template('choose_top_cadets.html', title='Выбор оценивающих по оси отношений',
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


@app.route('/transactions', methods=['GET'])
def transactions():
    data = Transaction.query.all()
    return render_template('transactions.html', title='Транзакции', data=data)


@app.route('/edit_profit_record', methods=['GET', 'POST'])
@login_required
def edit_profit_record():
    record_id = int(request.args.get('id'))
    record = Profit.query.get(record_id)
    form = FixProfit()
    if form.validate_on_submit():
        record.summa = float(form.profit.data)
        db.session.commit()
        # may be another actions
        return redirect('/profit_records')
    return render_template('edit_profit_record.html', title='Изменить значение прибыли', edit_form=form, record=record)


@app.route('/delete_profit_record', methods=['POST'])
@login_required
def delete_profit_record():
    record_id = int(request.args.get('id'))
    Profit.query.filter_by(id=record_id).delete()
    db.session.commit()
    # may be another actions
    return redirect('/profit_records')

@app.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    with open('app/static/json/citizenship.json', encoding='utf-8') as f:
        citizenship_json = f.read()
        
    with open('app/static/json/languages.json', encoding='utf-8') as f:
        languages_json = f.read()
        
    skills = Skill.query.filter_by(user_id=current_user.id).outerjoin(Skill.keywords).all()
    work_experience = WorkExperience.query.filter_by(user_id=current_user.id).all()
    user_languages = Language.query.filter_by(user_id=current_user.id).all()
    language_levels = ['A1 - начальный', 'A2 - ниже среднего', 'B1 - средний', 'B2 - выше среднего', 'C1 - продвинутый', 'C2 - профессиональный']
    
    return render_template('resume.html', user=current_user, citizenships=json.loads(citizenship_json),
                                          skills=skills, work_experience=work_experience,
                                          all_languages=json.loads(languages_json), language_levels=language_levels,
                                          user_languages=user_languages, title='Резюме')

@app.route('/api/skills', methods=['GET'])
@login_required
def get_skills():
    skills = Skill.query.filter_by(user_id=current_user.id).outerjoin(Skill.keywords).all()
    
    return json.dumps([{
        'id': skill.id,
        'title': skill.title,
        'keywords': [{
            'id': keyword.id,
            'value': keyword.value
            } for keyword in skill.keywords]
    } for skill in skills]), 200

@app.route('/api/skill/<id>/keywords')
@login_required
def get_skill_keywords(id):
    skill_keywords = SkillKeyword.query.filter_by(skill_id=id).all()
    
    return json.dumps([{
        'id': keyword.id,
        'value': keyword.value
    } for keyword in skill_keywords])

@app.route('/api/add-skill', methods=['POST'])
@login_required
def add_skill():
    data = request.json
    
    skill = Skill(title=data['title'], user_id=current_user.id)
    
    db.session.add(skill)
    db.session.commit()
    db.session.refresh(skill)
    
    for keyword in data['skill_keywords']:
        skill_keyword = SkillKeyword(value=keyword, skill_id=skill.id)
        db.session.add(skill_keyword)
        
    db.session.commit()
    
    return '', 201

@app.route('/api/remove-skill', methods=['POST'])
@login_required
def remove_skill():
    data = request.json
    
    Skill.query.filter_by(id=data['id'], user_id=current_user.id).delete()
    
    db.session.commit()
    
    return '', 200

@app.route('/api/work-exps', methods=['GET'])
@login_required
def get_work_exps():
    work_exps = WorkExperience.query.filter_by(user_id=current_user.id).all()
    
    return json.dumps([{
        'id': work_exp.id,
        'position': work_exp.position,
        'place': work_exp.place,
        'start_at': work_exp.start_at.isoformat(),
        'end_at': work_exp.end_at.isoformat() if work_exp.end_at else None
    } for work_exp in work_exps]), 200

@app.route('/api/work-exps/<id>')
@login_required
def get_work_exp(id):
    work_exp = WorkExperience.query.filter_by(id=id).first()
    
    return json.dumps({
        'id': work_exp.id,
        'position': work_exp.position,
        'place': work_exp.place,
        'start_at': work_exp.start_at.isoformat(),
        'end_at': work_exp.end_at.isoformat() if work_exp.end_at else None,
        'responsibilities': work_exp.responsibilities
    })

@app.route('/api/add-work-exp', methods=['POST'])
@login_required
def add_work_exp():
    data = request.json
    
    work_exp = WorkExperience(start_at=parser.parse(data['start_at']), end_at=data.get('end_at') and parser.parse(data['end_at']),
                              is_ended=data['is_ended'], place=data['place'], position=data['position'],
                              responsibilities=data['responsibilities'], user_id=current_user.id)
    
    db.session.add(work_exp)
    db.session.commit()
    
    return '', 201
    
@app.route('/api/remove-work-exp', methods=['POST'])
@login_required
def remove_work_exp():
    data = request.json
    
    WorkExperience.query.filter_by(id=data['id'], user_id=current_user.id).delete()
    
    db.session.commit()

    return '', 200

@app.route('/api/json/languages', methods=['GET'])
@login_required
def get_json_languages():
    with open('app/static/json/languages.json') as f:
        languages_json = f.read()
    
    return languages_json, 200

@app.route('/api/json/language-levels', methods=['GET'])
@login_required
def get_json_language_levels():
    return json.dumps(['A1 - начальный', 'A2 - ниже среднего', 'B1 - средний', 'B2 - выше среднего', 'C1 - продвинутый', 'C2 - профессиональный']), 200

@app.route('/api/languages', methods=['GET'])
@login_required
def get_languages():
    languages = Language.query.filter_by(user_id=current_user.id).all()
    
    return json.dumps([{
        'id': language.id,
        'name': language.name,
        'level': language.level
    } for language in languages]), 200

@app.route('/api/add-language', methods=['POST'])
@login_required
def add_language():
    data = request.json
    
    language = Language(name=data['name'], level=data['level'], user_id=current_user.id)
    
    db.session.add(language)
    db.session.commit()
    
    return '', 201

@app.route('/api/remove-language', methods=['POST'])
@login_required
def remove_language():
    data = request.json
    
    Language.query.filter_by(id=data['id'], user_id=current_user.id).delete()
    
    db.session.commit()
    
    return '', 200
    
@app.route('/api/change-language-name', methods=['POST'])
@login_required
def change_language_name():
    data = request.json
    
    language = Language.query.filter_by(id=data['id'], user_id=current_user.id).first()
    
    if not language:
        return 'Not Found', 404
    
    language.name = data['name']
    
    db.session.commit()
    
    return '', 200

@app.route('/api/change-language-level', methods=['POST'])
@login_required
def change_language_level():
    data = request.json
    
    language = Language.query.filter_by(id=data['id'], user_id=current_user.id).first()
    
    if not language:
        return 'Not Found', 404
    
    language.level = data['level']
    
    db.session.commit()
    
    return '', 200

@app.route('/api/change-resume', methods=['PATCH'])
@login_required
def change_resume():
    data = request.json
    
    if not (data.get('name') or len(data['name'])):
        return 'Invalid name', 400

    if not (data.get('surname') or len(data['surname'])):
        return 'Invalid surname', 400
    
    if data.get('sex') and (not len(data['sex']) or not data['sex'] in ['male', 'female']):
        return 'Invalid sex', 400
    
    user = User.query.filter_by(id=current_user.id).first()
    
    user.name = html.escape(data['name'])
    user.tg_nickname = html.escape(data['tg'])
    user.surname = html.escape(data['surname'])
    user.phone = html.escape(data['phone'])
    user.country = html.escape(data['country'])
    user.city = html.escape(data['city'])
    user.birthdate = parser.parse(data['birthdate']).strftime('%Y-%m-%d')
    user.sex = data['sex']
    user.citizenship = html.escape(data['citizenship'])
    user.description = html.escape(data['description'])
    
    db.session.commit()
    
    return '', 200

@app.route('/resumes')
@login_required
def resumes():
    cities = list(set([user.city for user in User.query.with_entities(User.city).all() if user.city and user.city.strip() != '']))
    
    return render_template('resumes.html', cities=cities, title='Резюме участников')

@app.route('/api/resumes')
@login_required
def get_resumes():
    take = request.args.get('take') or 7
    skip = request.args.get('skip') or 0
    
    select_males = request.args.get('selectMales') or 'true'
    select_females = request.args.get('selectFemales') or 'true'
    sex = []
    
    if select_males == 'true':
        sex.append('male')
    if select_females == 'true':
        sex.append('female')
    
    if (not request.args.get('selectMales')) and (not request.args.get('selectFemales')):
        sex = ['male', 'female']
    
    min_age = int(request.args.get('minAge') or 0)
    max_age = int(request.args.get('maxAge') or 1000)
    
    city = (request.args.get('city') or '').lower()
    search = (request.args.get('search') or '').lower()
    
    SECOND = 1000
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    YEAR = 365 * DAY
    
    is_with_no_experience = (request.args.get('selectWithoutWorkExp') or 'true') == 'true'
    no_experience_condition = """
        work_experience_in_ms != 0
    """ if not is_with_no_experience else "(1 = 1)"
    
    is_with_one_to_three_experience = (request.args.get('selectWithOneToThreeYears') or 'true') == 'true'
    one_to_three_experience_condition = f"""
        (
            work_experience_in_ms < {YEAR} OR
            work_experience_in_ms > {3 * YEAR}
        )
    """ if not is_with_one_to_three_experience else "(1 = 1)"
    
    is_with_three_to_six_experience = (request.args.get('selectWithThreeToSixYears') or 'true') == 'true'
    three_to_six_experience_condition = f"""
        (
            work_experience_in_ms < {3 * YEAR} OR
            work_experience_in_ms > {6 * YEAR}
        )
    """ if not is_with_three_to_six_experience else "(1 = 1)"
    
    is_with_six_and_more_experience = (request.args.get('selectWithSixAndMoreYears') or 'true') == 'true'
    six_and_more_experience_condition = f"""
        (
            work_experience_in_ms < {6 * YEAR}
        )
    """ if not is_with_six_and_more_experience else "(1 = 1)"
    
    search_condition = """
        (
            LOWER(job.position) LIKE :search OR
            LOWER(skill.title) LIKE :search OR
            LOWER(keyword.value) LIKE :search
        )
    """ if len(search) != 0 else "(1 = 1)"
    
    query = f"""
        FROM user
        LEFT JOIN work_experience job ON job.user_id = user.id
        LEFT JOIN skill ON skill.user_id = user.id
        LEFT JOIN skill_keyword keyword ON keyword.skill_id = skill.id
        WHERE
            sex IN (:first_sex_option, :second_sex_option) AND
            birthdate <= :min_age AND
            birthdate >= :max_age AND
            LOWER(city) LIKE :city AND
            {search_condition} AND
            {no_experience_condition} AND
            {one_to_three_experience_condition} AND
            {three_to_six_experience_condition} AND
            {six_and_more_experience_condition}
    """
    
    find_query = text(f"""
        SELECT
            DISTINCT(user.id), name, surname, birthdate,
            work_experience_in_ms
        {query}
        ORDER BY name
        LIMIT :limit
        OFFSET :offset
    """)
    
    count_query = text(f"""
        SELECT COUNT(DISTINCT(user.id))
        {query}
    """)
    
    query_options = {
        "first_sex_option": "male" if "male" in sex else "-1",
        "second_sex_option": "female" if "female" in sex else "-1",
        "min_age": (datetime.datetime.now() - relativedelta(years=min_age)).strftime('%Y-%m-%d'),
        "max_age": (datetime.datetime.now() - relativedelta(years=max_age)).strftime('%Y-%m-%d'),
        "city": f"%{city}%",
        "search": f"%{search}%",
        "limit": int(take),
        "offset": int(skip)
    }
    
    find_jobs_query = text("""
        SELECT id, place, position, start_at, end_at
        FROM work_experience job
        WHERE job.user_id = :user_id
    """)
    
    find_skills_query = text("""
        SELECT id, title
        FROM skill
        WHERE skill.user_id = :user_id
    """)
    
    find_keywords_query = text("""
        SELECT id, value
        FROM skill_keyword keyword
        WHERE keyword.skill_id = :skill_id
    """)
    
    resumes = [dict(resume) for resume in db.engine.execute(find_query, query_options)]
    count = list(db.engine.execute(count_query, query_options))[0][0]
    
    for resume in resumes:
        user = User.query.filter_by(id=resume['id']).first()
        update_work_experience(user)
        resume['work_experience_in_ms'] = user.work_experience_in_ms
        
        resume['match'] = None
        
        jobs = [dict(job) for job in db.engine.execute(find_jobs_query, {
            "user_id": resume['id']
        })]
        
        for job in jobs:
            if search in job['position'].lower():
                resume['match'] = 'position'
        
        resume['jobs'] = jobs
        
        skills = [dict(skill) for skill in db.engine.execute(find_skills_query, {
            "user_id": resume['id']
        })]
        
        for skill in skills:            
            keywords = [dict(keyword) for keyword in db.engine.execute(find_keywords_query, {
                "skill_id": skill['id']
            })]
            
            for keyword in keywords:
                if search in keyword['value'].lower():
                    resume['match'] = 'skill_keyword'
            
            if search in skill['title'].lower():
                resume['match'] = 'skill'
            
            skill['keywords'] = keywords
        
        resume['skills'] = skills
        
    return json.dumps({
        'total': count,
        'data': [ {
            'id': resume['id'],
            'name': resume['name'],
            'surname': resume['surname'],
            'birthdate': resume['birthdate'].isoformat() if resume['birthdate'] else None,
            'work_experience_in_ms': resume['work_experience_in_ms'],
            'match': resume['match'],
            'jobs': [ {
                'id': job['id'],
                'place': job['place'],
                'position': job['position'],
                'start_at': job['start_at'].isoformat(),
                'end_at': job['end_at'].isoformat() if job['end_at'] else None
                } for job in resume['jobs'] ],
            'skills': [{
                'id': skill['id'],
                'title': skill['title'],
                'keywords': [{
                    'id': keyword['id'],
                    'value': keyword['value']
                    } for keyword in skill['keywords']]
                } for skill in resume['skills']],
            } for resume in resumes
        ]
    })
    
@app.route('/resume/<id>')
@login_required
def view_resume(id):
    user = User.query.filter_by(id=id).first()
    
    skills = Skill.query.filter_by(user_id=user.id).outerjoin(Skill.keywords).all()
    work_experience = WorkExperience.query.filter_by(user_id=user.id).all()
    user_languages = Language.query.filter_by(user_id=user.id).all()
    
    return render_template('view_resume.html', user=user, skills=skills,
                           work_experience=work_experience,
                           user_languages=user_languages, title='Резюме участника')

def update_work_experience(user):
    jobs = [job.__dict__ for job in WorkExperience.query.filter_by(user_id=user.id).all()]
    jobs = merge_intervals(jobs)
    
    experience_in_ms = 0
    for job in jobs:
        experience_in_ms += ((job['end_at'] or datetime.date.today()) - job['start_at']).total_seconds() * 1000
        
    user.work_experience_in_ms = experience_in_ms
    
    db.session.commit()

def merge_intervals(intervals):
    merged = []
    
    for interval in sorted(intervals, key=lambda x: x['start_at'] or datetime.date.max):
        normalized_interval = { 'start_at': interval['start_at'], 'end_at': interval['end_at'] }
        
        if len(merged) == 0:
            merged.append(normalized_interval)
            continue
        
        last_end_at = merged[-1]['end_at'] or datetime.date.max
        current_end_at = interval['end_at'] or datetime.date.max
        
        is_overlap = interval['start_at'] <= last_end_at and last_end_at <= current_end_at
        is_contained = merged[-1]['start_at'] <= interval['start_at'] and current_end_at <= last_end_at
        
        if is_overlap or is_contained:
            merged_interval = {
                'start_at': min(interval['start_at'], merged[-1]['start_at']),
                'end_at': None
                    if (merged[-1]['end_at'] == None or interval['end_at'] == None)
                    else max(current_end_at, last_end_at)
            }
            
            merged.pop()
            merged.append(merged_interval)
        else:
            merged.append(normalized_interval)

    return merged