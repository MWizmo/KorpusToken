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
w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))

kti_address = '0xa47286dd2496e4b6d389fbeb2879db8f3bcb5697'
ktd_address = '0x99d01e76234cd97a6bcc43664e6bc4c49d11524a'
contract_address = '0x96d0925e383c658d9ab0e90679e866d9cf2c7614'
ETH_IN_WEI = 1000000000000000000
KT_BITS_IN_KT = 1000000000000000000

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models
from app import token_utils
from app.token import routes
from app.admin.views import MyAdminIndexView, TransactionView, AllBudgetRecordsView, CurrentBudgetView

admin = Admin(app, name='Korpus Token', index_view=MyAdminIndexView(url='/'), template_mode='bootstrap3')
admin.add_view(TransactionView(models.Transaction, db.session, name='Транзакции', endpoint='transactions'))
admin.add_view(AllBudgetRecordsView(models.BudgetRecord, db.session, name='Все записи', endpoint='all_budget_records'))
admin.add_view(CurrentBudgetView(models.BudgetRecord, db.session, name='Текущий бюджет', endpoint='current_budget'))

jobstores = {
    'default': SQLAlchemyJobStore(url=os.environ.get('DATABASE_URI')\
        or 'mysql+pymysql://korpus_user:korpus_password@localhost/korpus_db_test')
}

job_defaults = {
    'coalesce': False,
    'max_instances': 1
}

scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)
scheduler.start()
if len(scheduler.get_jobs()) == 0:
    scheduler.add_job(func=token_utils.set_token_price, max_instances=1, trigger='cron', day='1')
atexit.register(lambda: scheduler.shutdown())