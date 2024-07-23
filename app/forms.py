
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User
from config import Config


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignupForm(FlaskForm):
    email = StringField('Почта:', validators=[DataRequired(), Email()])
    tg_nickname = StringField('Ник в Telegram:', validators=[DataRequired()])
    login = StringField('Логин для авторизации:', validators=[DataRequired()])
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль: ', validators=[DataRequired(), EqualTo('password')])
    courses = StringField('Пройденные курсы в IT-Korpus:')
    participate = BooleanField('Членство в IT-Korpus ')
    team = SelectField('Название команды:', choices=[*Config.TEAMS])
    role = SelectField('Роль в команде:', choices=[*Config.ROLES])
    birthday = DateField('Дата рождения: ')
    sex = SelectField('Пол:', choices=[('man', 'Мужчина'), ('woman', 'Женщина')])
    vk_url = StringField('Ссылка на профиль ВКонтакте:', validators=[DataRequired()])
    fb_url = StringField('Ссылка на профиль Фейсбук:', validators=[DataRequired()])
    inst_url = StringField('Ссылка на профиль Инстаграм:', validators=[DataRequired()])
    work_exp = StringField('Опыт работы: ')
    education = StringField('Место учебы: ')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Логин занят')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email занят')
