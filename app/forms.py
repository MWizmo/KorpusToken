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
    email = StringField('Почта:', validators=[DataRequired(), Email()])
    tg_nickname = StringField('Ник в Telegram:', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    login = StringField('Логин для авторизации:', validators=[DataRequired()])
    password = PasswordField('Пароль: ', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль: ', validators=[DataRequired(), EqualTo('password')])
    courses = StringField('Пройденные курсы в IT-Korpus:')
    participate = BooleanField('Я участвую в проекте Корпуса')
    team = SelectField('Название команды:', choices=[*SuppClass.get_teams()])
    #role = SelectField('Роль в команде:', choices=[*Config.ROLES])
    birthday = DateField('Дата рождения: ', render_kw={"placeholder": "YYYY-MM-DD"})
    sex = SelectField('Пол:', choices=[('man', 'Мужчина'), ('woman', 'Женщина')])
    vk_url = StringField('Ссылка на профиль ВКонтакте:', validators=[DataRequired()])
    fb_url = StringField('Ссылка на профиль Фейсбук:', validators=[DataRequired()])
    inst_url = StringField('Ссылка на профиль Инстаграм:', validators=[DataRequired()])
    work_exp = TextAreaField('Опыт работы: ')
    education = StringField('Образование: ')
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Логин занят')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email занят')


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
    question_form = TextAreaField('Вопрос', validators=[DataRequired()])
    question_type = IntegerField('Тип вопроса', validators=[DataRequired()])
    submit = SubmitField('Создать')


class TeamAdding(FlaskForm):
    title = StringField('Название команды', validators=[DataRequired()],
                        render_kw={"placeholder": "Название новой команды"})
    submit = SubmitField('Добавить')


class MemberAdding(FlaskForm):
    name = StringField('Новый участник команды', validators=[DataRequired()])
    submit = SubmitField('Добавить')
