from app import app, db
from app.scripts.service import get_access
from app.models import User
from flask import render_template, redirect, url_for, request, jsonify, send_file, flash
from flask_login import current_user, login_required
from app.token.forms import *
import app.token.utils as token_utils
from app.routes import log


@app.route('/accounting', methods=['GET', 'POST'])
@login_required
def accounting():
    if not (User.check_admin(current_user.id) or User.check_chieftain(current_user.id)):
        log('Попытка просмотра страницы с бухгалтерией (ГВ)')
        return render_template('gryazniy_vzlomshik.html', access=get_access(current_user))
    log('Просмотр страницы бухгалтерии')
    send_ktd_form = CreateKTDForm()
    send_kti_form = CreateKTIForm()
    send_eth_form = CreateEthForm()
    set_budget_form = SetBudgetForm()
    put_mark_form = PutMarkForm()
    exchange_ktd_to_eth_form = ExchangeKTDToEthForm()
    if send_ktd_form.send_ktd.data and send_ktd_form.validate():
        res, status = token_utils.createKTD(send_ktd_form.num.data, send_ktd_form.receiver.data)
        flash(res, 'send_ktd')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'send_ktd')
        return redirect(url_for('accounting'))
    if send_kti_form.send_kti.data and send_kti_form.validate():
        res, status = token_utils.createKTI(send_kti_form.num.data, send_kti_form.receiver.data)
        flash(res, 'send_kti')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'send_kti')
        return redirect(url_for('accounting'))
    if send_eth_form.send_eth.data and send_eth_form.validate():
        res, status = token_utils.transferWEI(send_eth_form.num.data, send_eth_form.receiver.data)
        flash(res, 'send_eth')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'send_eth')
        return redirect(url_for('accounting'))
    if set_budget_form.set_budget.data and set_budget_form.validate():
        date = set_budget_form.date.data.replace('.','')
        res, status = token_utils.setBudget(date, set_budget_form.subject.data, set_budget_form.price.data)
        flash(res, 'set_budget')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'set_budget')
        return redirect(url_for('accounting'))
    if set_budget_form.get_budget.data and set_budget_form.validate():
        date = set_budget_form.date.data.replace('.', '')
        cost = token_utils.getBudget(date, set_budget_form.subject.data)
        flash(cost, 'get_budget')
    if put_mark_form.put_mark.data and put_mark_form.validate():
        date = put_mark_form.date.data.replace('.', '')
        res, status = token_utils.setStudentResult(put_mark_form.project.data, put_mark_form.student.data, date,
                                           put_mark_form.criterion.data, int(put_mark_form.mark.data))
        flash(res, 'put_mark')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'put_mark')
        return redirect(url_for('accounting'))
    if put_mark_form.get_mark.data and put_mark_form.validate():
        date = put_mark_form.date.data.replace('.', '')
        mark = token_utils.getStudentResults(put_mark_form.project.data, put_mark_form.student.data, date,
                                           put_mark_form.criterion.data)
        flash(mark, 'get_mark')
    if exchange_ktd_to_eth_form.exchange_ktd_to_eth.data and exchange_ktd_to_eth_form.validate():
        res, status = token_utils.sellKTD(exchange_ktd_to_eth_form.num.data)
        flash(res, 'exchange_ktd_to_eth')
        if status:
            flash("https://ropsten.etherscan.io/tx/" + status, 'exchange_ktd_to_eth')
    return render_template('accounting.html', title='Korpus Бухгалтерия',
                           access=get_access(current_user), send_ktd_form=send_ktd_form, send_kti_form=send_kti_form,
                           send_eth_form=send_eth_form, set_budget_form=set_budget_form, put_mark_form=put_mark_form,
                           exchange_ktd_to_eth_form=exchange_ktd_to_eth_form)