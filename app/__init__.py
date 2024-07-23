from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from web3.auto import Web3
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os
import atexit

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
infura_url = "https://polygon-amoy.infura.io/v3/35b77298442b49168bbe5a150071dd9f"
chain_id = 80002
w3 = Web3(Web3.HTTPProvider(infura_url))

kti_address = '0x0E67be48db95B6BA01265eCF67C2D2a453ff485c'
ktd_address = '0x69084e921F355b70336698A4Bd04cAb9E2A5541A'
contract_address = '0xceb8E63CF6E7AD8680Ccb6B13685E65755c3C8cC'
ETH_IN_WEI = 1000000000000000000
KT_BITS_IN_KT = 1000000000000000000

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import models
from app import token_utils
from app.token import routes
from app.routes import common_routes, questionnaire_routes, voting_routes
from app.admin.views import MyAdminIndexView, TransactionView, AllBudgetRecordsView, CurrentBudgetView, ProfitRecordView

admin = Admin(app, name='Korpus Token', index_view=MyAdminIndexView(url='/'), template_mode='bootstrap3')
admin.add_view(TransactionView(models.Transaction, db.session, name='Транзакции', endpoint='transactions'))
admin.add_view(ProfitRecordView(models.Profit, db.session, name='Зафиксированная прибыль', endpoint='profit_records'))
admin.add_view(AllBudgetRecordsView(models.BudgetRecord, db.session, name='Все записи', endpoint='all_budget_records'))
admin.add_view(CurrentBudgetView(models.BudgetRecord, db.session, name='Текущий бюджет', endpoint='current_budget'))

jobstores = {
    'default': SQLAlchemyJobStore(url=Config.SQLALCHEMY_DATABASE_URI)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)
scheduler.start()
if len(scheduler.get_jobs()) < 2:
    scheduler.add_job(func=token_utils.set_token_price, max_instances=1, trigger='cron', day='1')
    scheduler.add_job(func=models.User.remove_rejected_users, max_instances=1, trigger='cron', day="*")
atexit.register(lambda: scheduler.shutdown())
