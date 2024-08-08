from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from web3.auto import Web3
from apscheduler.schedulers.background import BackgroundScheduler
import os
import atexit

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
infura_url = os.environ['INFURA_URL']
chain_id = 137
w3 = Web3(Web3.HTTPProvider(infura_url))

kti_address = '0xB21c482806E3a9849dfFCCe244C1e0ABadEA9cE5'
ktd_address = '0x99069AcF6a4E06f9964E2D2c7E31dCf17b3486Bd'
contract_address = '0x3358dc0D74A4F738440B78C6a6005161dd9d3BA1'
ETH_IN_WEI = 1e18
KT_BITS_IN_KT = 1e18

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

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

scheduler = BackgroundScheduler(job_defaults=job_defaults)
scheduler.start()
scheduler.add_job(func=token_utils.set_token_price, max_instances=1, trigger='cron', day='1')
scheduler.add_job(func=models.User.remove_rejected_users, max_instances=1, trigger='cron', day="*")
atexit.register(lambda: scheduler.shutdown())
