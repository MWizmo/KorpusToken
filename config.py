import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql+pymysql://sammy:password@localhost/korpus_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ROLES = [('1', 'Front-end'), ('2', 'Проженный'), ('3', 'Рядовой'), ('4', 'Желторотик')]

    """
    При добавлении статусов в бд обязательно соблюсти следующие отношения:
    id 1 Админ
    id 2 Атаман
    id 3 Курсант
    id 4 Тимлид
    Иначе система определения статуса сломается.
    """
