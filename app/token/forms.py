# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class CreateKTDForm(FlaskForm):
    receiver = StringField('Адрес кошелька получателя', validators=[DataRequired()])
    num = StringField('Количество токенов вклада', validators=[DataRequired()])
    send_ktd = SubmitField('Отправить')


class CreateKTIForm(FlaskForm):
    receiver = StringField('Адрес кошелька получателя', validators=[DataRequired()])
    num = StringField('Количество токенов инвестиции', validators=[DataRequired()])
    send_kti = SubmitField('Отправить')


class CreateEthForm(FlaskForm):
    receiver = StringField('Адрес кошелька получателя', validators=[DataRequired()])
    num = StringField('Количество эфира', validators=[DataRequired()])
    send_eth = SubmitField('Отправить')


class SetBudgetForm(FlaskForm):
    date = StringField('Дата', validators=[DataRequired()])
    subject = StringField('Статья расхода', validators=[DataRequired()])
    price = StringField('Стоимость')
    set_budget = SubmitField('Зафиксировать')
    get_budget = SubmitField('Узнать стоимость')


class PutMarkForm(FlaskForm):
    date = StringField('Дата (ДД.ММ.ГГГГ)', validators=[DataRequired()])
    project = StringField('Название проекта', validators=[DataRequired()])
    student = StringField('ФИО курсанта', validators=[DataRequired()])
    criterion = StringField('Критерий', validators=[DataRequired()])
    mark = IntegerField('Оценка')
    put_mark = SubmitField('Зафиксировать оценку')
    get_mark = SubmitField('Узнать оценку')


class ExchangeKTDToEthForm(FlaskForm):
    num = StringField('Число токенов для обмена', validators=[DataRequired()])
    exchange_ktd_to_eth = SubmitField('Обменять')