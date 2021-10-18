# -*- coding: utf-8 -*-
import os


class Config(object):
    SECRET_KEY = 'korpus_token_secret_key'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'mysql+pymysql://korpus_user:korpus_password@localhost/korpus_db_test'

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
		id 8 Бухгалтер
    Иначе система определения статуса сломается.
    
    При добавлении осей в бд обязательно соблюсти следующие отношения:
    id 1 Отношений
    id 2 Дела
    id 3 Власти
    Иначе система определения осей сломается.
    
    При добавлении ролей в бд обязательно соблюсти следующие отношения:
    id 1 Тимлид
    Иначе система определения ролей сломается.
    
    insert into teams values (1, 'FirstTeam', 0), (2, 'SecondTeam', 0), (3, 'ThirdTeam', 0), 
                             (4, 'FourthTeam', 1), (5, 'FifthTeam', 1), (6, 'SixthTeam', 1);
    
    insert into statuses values (1, 'Админ'), (2, 'Атаман'), (3, 'Курсант'), (4, 'Тимлид'), 
                                (5, 'Трекер'), (6, 'Эксперт'), (7, 'Топ-курсант'), (8, 'Бухгалтер');
                                
    insert into axis values (1, 'Отношений', 0), (2, 'Дела', 0), (3, 'Власти', 0);
    
    """


# url?name=value&name=value