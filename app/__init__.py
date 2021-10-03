from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from web3.auto import Web3


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))

kti_address = '0x1962a99aa03b1db4f48f7efc52d07705d3a860b0'
ktd_address = '0x6df020997384117b6128de28339a0b32e20af00a'
contract_address = '0x6ba9439286362d67b1f37fc95d18247ce931451d'
ETH_IN_WEI = 1000000000000000000

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models
from app.token import routes
from app.admin.views import MyAdminIndexView, TransactionView, AllBudgetRecordsView, CurrentBudgetView

admin = Admin(app, name='Korpus Token', index_view=MyAdminIndexView(url='/'), template_mode='bootstrap3')
admin.add_view(TransactionView(models.Transaction, db.session, name='Транзакции', endpoint='transactions'))
admin.add_view(AllBudgetRecordsView(models.BudgetRecord, db.session, name='Все записи', endpoint='all_budget_records'))
admin.add_view(CurrentBudgetView(models.BudgetRecord, db.session, name='Текущий бюджет', endpoint='current_budget'))