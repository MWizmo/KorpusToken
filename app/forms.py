# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    DateField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User, Teams
from config import Config


class SuppClass:
    @staticmethod
    def get_teams():
        teams = []
        for team in Teams.query.all():
            teams.append((str(team.id), team.name))
        return teams


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignupForm(FlaskForm):
    email = StringField('Почта:')
    tg_nickname = StringField('Ник в Telegram:', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин для авторизации:', validators=[DataRequired()])
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль: ', validators=[DataRequired(), EqualTo('password')])
    courses = StringField('Пройденные курсы в IT-Korpus:')
    participate = BooleanField('Я участвую в проекте Корпуса')
    #team = SelectField('Название команды:', choices=[*SuppClass.get_teams()])
    birthday = DateField('Дата рождения: ', render_kw={"placeholder": "YYYY-MM-DD"})
    sex = SelectField('Пол:', choices=[('man', 'Мужчина'), ('woman', 'Женщина')])
    vk_url = StringField('Ссылка на профиль ВКонтакте:')
    fb_url = StringField('Ссылка на профиль Фейсбук:')
    inst_url = StringField('Ссылка на профиль Инстаграм:')
    work_exp = TextAreaField('Опыт работы: ')
    education = StringField('Образование: ')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Логин занят')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Email занят')


class ProfileForm(FlaskForm):
    tg_nickname = StringField('Ник в Telegram:', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    courses = StringField('Пройденные курсы в IT-Korpus:')
    participate = BooleanField('Я участвую в проекте Корпуса')
    birthday = DateField('Дата рождения: ', render_kw={"placeholder": "YYYY-MM-DD"})
    sex = SelectField('Пол:', choices=[('man', 'Мужчина'), ('woman', 'Женщина')])
    vk_url = StringField('Ссылка на профиль ВКонтакте:', validators=[DataRequired()])
    fb_url = StringField('Ссылка на профиль Фейсбук:', validators=[DataRequired()])
    inst_url = StringField('Ссылка на профиль Инстаграм:', validators=[DataRequired()])
    work_exp = TextAreaField('Опыт работы: ')
    education = StringField('Образование: ')
    submit = SubmitField('Зарегистрироваться')


class RestorePassword(FlaskForm):
    login = StringField('Логин в системе:', validators=[DataRequired()])
    password = PasswordField('Новый пароль: ', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль: ', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Отправить')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is None:
            raise ValidationError('Пользователь с таким логином не найден')


class QuestionnairePersonal(FlaskForm):
    qst_personal_growth = TextAreaField('Личностный рост ', validators=[DataRequired()])
    qst_controllability = TextAreaField('Управляемость ', validators=[DataRequired()])
    qst_selfcontrol = TextAreaField('Самоуправление ', validators=[DataRequired()])
    qst_strategy = TextAreaField('Стратегия ', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class QuestionnaireTeam(FlaskForm):
    qst_q1 = StringField('', validators=[DataRequired()])
    qst_q2 = StringField('', validators=[DataRequired()])
    qst_q3 = StringField('', validators=[DataRequired()])
    qst_q4 = StringField('', validators=[DataRequired()])
    qst_q5 = StringField('', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class QuestionAdding(FlaskForm):
    question_1 = TextAreaField('Вопрос 1')
    question_2 = TextAreaField('Вопрос 2')
    question_3 = TextAreaField('Вопрос 3')
    question_4 = TextAreaField('Вопрос 4')
    question_5 = TextAreaField('Вопрос 5')
    submit = SubmitField('Изменить')


class TeamAdding(FlaskForm):
    title = StringField('Название команды', validators=[DataRequired()],
                        render_kw={"placeholder": "Название новой команды"})
    type = SelectField('Тип команды:', choices=[('1', 'Оценивается'), ('2', 'Не оценивается'), ('3', 'Состояние не определено'),
                                                ('4', 'Участвует в еженедельной оценке')])
    submit = SubmitField('Добавить')


class MemberAdding(FlaskForm):
    name = StringField('Новый участник команды', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class ChooseTeamForm(FlaskForm):
    team = StringField('Выберите команду', validators=[DataRequired()])
    submit = SubmitField('Выбрать')


class StartAssessmentForm(FlaskForm):
    month1 = StringField('Укажите, за какой период проводится оценка', validators=[DataRequired()])
    month2 = StringField('Укажите, за какой период проводится оценка', validators=[DataRequired()])
    submit = SubmitField('Начать оценку',render_kw={"class": "nav__link border"})

class ChangeAddress(FlaskForm):
    new_private_key = StringField('Укажите приватный ключ вашего кошелька ethereum', validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%"})

class TransferKtdForm(FlaskForm):
    num = StringField(validators=[DataRequired()])
    address = StringField(validators=[DataRequired()])


class AddBudgetItemForm(FlaskForm):
    item = StringField(validators=[DataRequired()])
    cost = StringField(validators=[DataRequired()])

class ManageKTIForm(FlaskForm):
    address = StringField(validators=[DataRequired()])
    num = StringField(validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%; margin-top: 2rem"})

class ManageKTDForm(FlaskForm):
    address = StringField(validators=[DataRequired()])
    num = StringField(validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%; margin-top: 2rem"})

class ChangeToEthForm(FlaskForm):
    amount = StringField(validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%; margin-top: 2rem"})

class ChangeEthExchangeRate(FlaskForm):
    price = StringField('Напишите актуальную стоимость 1 eth', validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%; margin-top: 2rem"})

class FixProfit(FlaskForm):
    profit = StringField('Введите объём полученных средств в рублях', validators=[DataRequired()])
    submit = SubmitField('Подтвердить', render_kw={"class": "eth_button", "style": "width: 50%; margin-left: 25%; margin-top: 2rem"})