import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql+pymysql://sammy:password@localhost/korpus_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ROLES = [('1', 'Front-end'), ('2', 'Проженный'), ('3', 'Рядовой'), ('4', 'Желторотик')]
    TEAMS = [('ZELTOROTIKI','ZELTOROTIKI'), ('MARSIANE', 'MARSIANE'), ('RUSSIANS', 'RUSSIANS')]
