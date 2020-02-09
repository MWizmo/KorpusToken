# -*- coding: utf-8 -*-
import os


class Config(object):
    SECRET_KEY = 'korpus_token_secret_key'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
    or 'mysql+pymysql://non-root:123@localhost/korpus_db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ROLES = [('1', 'Front-end'), ('2', 'Проженный'), ('3', 'Рядовой'), ('4', 'Желторотик')]

    """
    При добавлении статусов в бд обязательно соблюсти следующие отношения:
    id 1 Админ
    id 2 Атаман
    id 3 Курсант
    id 4 Тимлид
    id 5 Трекер
    id 6 Эксперт
    id 7 Топ-курсант
    Иначе система определения статуса сломается.
    
    При добавлении осей в бд обязательно соблюсти следующие отношения:
    id 1 Отношений
    id 2 Дела
    id 3 Власти
    Иначе система определения осей сломается.
    
    При добавлении ролей в бд обязательно соблюсти следующие отношения:
    id 1 Тимлид
    Иначе система определения ролей сломается.
    """


# url?name=value&name=value