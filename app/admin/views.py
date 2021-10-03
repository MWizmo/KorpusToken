from flask_admin import AdminIndexView, expose
from flask_login import current_user
from flask import redirect, render_template, jsonify, request
from app.models import *
from datetime import datetime, date, timedelta
from app import db
from flask_admin.contrib.sqla import ModelView
import datetime, calendar
import locale
locale.setlocale(locale.LC_ALL, '')


class MyAdminIndexView(AdminIndexView):
    pass
    # @expose('/transactions')
    # def index(self):
    #     return redirect('/admin/users')  # super(MyAdminIndexView, self).index()
    #
    # @expose('users/profile/<uid>')
    # def profile(self, uid):
    #     user = Users.query.filter_by(id=uid).first()
    #     if user:
    #         return render_template('admin/user_profile.html', user=user)
    #     else:
    #         return redirect('admin/users')
    #
    # @expose('payments_per_month')
    # def payments_per_month(self):
    #     res = db.session.query(db.func.sum(Payments.amount)).filter(
    #         Payments.payment_date.between(datetime(datetime.now().year, datetime.now().month,
    #                                    datetime.now().day, datetime.now().hour, datetime.now().minute) - timedelta(30),
    #                               datetime(datetime.now().year, datetime.now().month,
    #                                    datetime.now().day, datetime.now().hour, datetime.now().minute))).scalar()
    #     return jsonify({'amount': res})
    #
    # @expose('summary_payments')
    # def summary_payments(self):
    #     res = db.session.query(db.func.sum(Payments.amount)).scalar()
    #     return jsonify({'amount': res})
    #
    # @expose('products/')
    # def products(self):
    #     # lal_summary = LalTasks.query.with_entities(LalTasks.user_id).distinct().count()
    #     # lal_per_month = LalTasks.query.with_entities(LalTasks.user_id).filter(
    #     #     LalTasks.started_at.between(date(datetime.now().year, datetime.now().month,
    #     #                                      datetime.now().day) - timedelta(30),
    #     #                                 date(datetime.now().year, datetime.now().month,
    #     #                                      datetime.now().day))).distinct().count()
    #     # an_summary = AnalyticsTasks.query.with_entities(AnalyticsTasks.user_id).distinct().count()
    #     # an_per_month = AnalyticsTasks.query.with_entities(AnalyticsTasks.user_id).filter(
    #     #     AnalyticsTasks.started_at.between(date(datetime.now().year, datetime.now().month,
    #     #                                            datetime.now().day) - timedelta(30),
    #     #                                       date(datetime.now().year, datetime.now().month,
    #     #                                            datetime.now().day))).distinct().count()
    #     # return render_template('admin/products.html', lal_summary=lal_summary, an_summary=an_summary,
    #     #                        lal_per_month=lal_per_month, an_per_month=an_per_month)
    #     return render_template('admin/products.html')
    #
    # @expose('get_rates')
    # def get_rates(self):
    #     lal_rate = Products.query.get(1).default_rate
    #     an_rate = Products.query.get(2).default_rate
    #     ban_rate = Products.query.get(3).default_rate
    #     return jsonify({'lal_rate': lal_rate, 'an_rate': an_rate, 'ban_rate': ban_rate})
    #
    # @staticmethod
    # def update_default_rates(product_id, old_rate, new_rate):
    #     rates = Rates.query.all()
    #     for r in rates:
    #         if product_id == 1 and r.lal_rate == old_rate:
    #             r.lal_rate = new_rate
    #         elif product_id == 2 and r.analysis_rate == old_rate:
    #             r.analysis_rate = new_rate
    #         elif product_id == 3 and r.banner_rate == old_rate:
    #             r.banner_rate = new_rate
    #     db.session.commit()
    #
    # @expose('change_rate', methods=['POST'])
    # def change_rate(self):
    #     product_id = int(request.json.get('product_id'))
    #     new_rate = float(request.json.get('rate'))
    #     product = Products.query.get(product_id)
    #     if new_rate != product.default_rate:
    #         self.update_default_rates(product_id, product.default_rate, new_rate)
    #         product.default_rate = new_rate
    #         db.session.commit()
    #     return jsonify({'answer': 'ok'})


class TransactionView(ModelView):
    list_template = 'transactions.html'
    column_exclude_list = ['id']
    column_labels = {'date': 'Дата', 'type': 'Тип операции', 'summa': 'Сумма',
                     'receiver': 'Контрагент', 'status': 'Статус'}
    can_edit = False
    can_create = False
    can_delete = False


class AllBudgetRecordsView(ModelView):
    list_template = 'all_budget_records.html'
    column_exclude_list = ['id']
    column_labels = {'date': 'Дата', 'item': 'Статья', 'summa': 'Сумма',
                     'who_added': 'Кто добавил'}
    can_edit = False
    can_create = False
    can_delete = False


class CurrentBudgetView(ModelView):
    list_template = 'current_budget.html'
    column_exclude_list = ['id']
    column_labels = {'date': 'Дата', 'item': 'Статья', 'summa': 'Сумма',
                     'who_added': 'Кто добавил'}
    can_edit = False
    can_create = False
    can_delete = False

    def render(self, template, **kwargs):
        today = datetime.date.today()
        month_dict = {'Dec': 'декабрь', 'Jan': 'январь', 'Feb': 'февраль', 'Mar': 'март', 'Apr': 'апрель', 'May': 'май',
                      'Jun': 'июнь', 'Jul': 'июль', 'Aug': 'август', 'Sep': 'сентябрь', 'Oct': 'октябрь',
                      'Nov': 'ноябрь'}
        kwargs['month'] = month_dict[calendar.month_abbr[today.month % 12 + 1]]
        return super(CurrentBudgetView, self).render(template, **kwargs)

