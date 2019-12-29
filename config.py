import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'mysql://root@localhost/korpus_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ROLES = [('Front-end', 'Front-end'), ('Prozzenniy', 'Проженный'), ('Private', 'Рядовой'), ('Jeltorotik', 'Желторотик')]
    TEAMS = [('Jeltorotiki','Желторотики'), ('Beatles', 'Beatles'), ('Nirvana', 'Nirvana'), ('5A', '5А')]
