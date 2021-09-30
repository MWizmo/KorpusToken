from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models
from app.token import routes
from app.admin.views import MyAdminIndexView, TransactionView, AllBudgetRecordsView, CurrentBudgetView

admin = Admin(app, name='Korpus Token', index_view=MyAdminIndexView(url='/'), template_mode='bootstrap3')
admin.add_view(TransactionView(models.Transaction, db.session, name='Транзакции', endpoint='transactions'))
admin.add_view(AllBudgetRecordsView(models.BudgetRecord, db.session, name='Все записи', endpoint='all_budget_records'))
admin.add_view(CurrentBudgetView(models.BudgetRecord, db.session, name='Текущий бюджет', endpoint='current_budget'))