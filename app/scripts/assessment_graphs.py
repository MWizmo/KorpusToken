# библиотека для рисования графов.
import networkx as nx
import os
from app import app
# библиотека с методами для строк.
import string
# импорт необходимого метода, с помощью которого можно пробегаться по алфавиту.
from string import ascii_uppercase
# вспомогательная библиотека для визуализации графов.
import matplotlib.pyplot as plt
# библиотека для октрытия гугл таблиц на диске.
import gspread
# библиотека для авторизации в гугле.
from oauth2client.service_account import ServiceAccountCredentials
# метод для нахождения моды.
from statistics import mode
from flask import url_for

class Forms_and_graphs:
    @staticmethod
    def private_form(name, questions_private, answers_private):
        # название таблицы на гугл диске.
        form = "Оценка вклада"
        # название листа в таблице.
        worksht = "Лист1"
        # настройка необходимых разрешений апи для гугла.
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        # чтение файла с данными о сервисном аккаунте, через который скрипт открывает и редактирует таблицу.
        # необходимо иметь файл Korpus Token-616b37e6af5d.json в папке со скриптом, либо указать до него путь.
        credentials = ServiceAccountCredentials.from_json_keyfile_name("Korpus Token-616b37e6af5d.json", scope)
        # авторизация в гугле.
        gc = gspread.authorize(credentials)
        # открываем таблицу.
        sh = gc.open(form)
        # открываем лист в таблице.
        worksheet = sh.worksheet(worksht)
        # указываем строку, с которой будет начинаться работа.
        line = 2
        # вставляем в ячейки A2, A3, A4... AN вопросы из индивидуальной анкеты, в зависимости от их количества.
        for i in range(len(questions_private)):
            # запись данных в ячейку.
            worksheet.update_acell('A' + str(line), questions_private[i])
            # переход на следующую строку.
            line += 1
        x = 0
        # ищем первую пустую ячейку, переходя по полям вправо.
        # поле, в котором находится эта ячейка и будет свободным полем для записи.
        while worksheet.acell(string.ascii_uppercase[x] + '1').value != "":
            x += 1
        # записываем в данную ячейку имя заполнителя анкеты.
        worksheet.update_acell(string.ascii_uppercase[x] + '1', name)
        # указываем строку с которой ведётся работа.
        line = 2
        # в найденное пустое поле вводим ответы на вопросы заполнителя личной анкеты.
        for i in range(len(answers_private)):
            # заполняем ячейку.
            worksheet.update_acell(string.ascii_uppercase[x] + str(line), answers_private[i])
            # переносим строку, чтобы заполнить следующую ячейку.
            line += 1

    @staticmethod
    def command_form(questions_command, answers_command, team_id, date):
        # список связей.
        edges_list = []
        # список нод, на которые указавыают стрелки.
        arrow_receivers = []
        # список нод, из которых стрелки исходят.
        arrow_senders = []
        # словарь подписей нод в виде Нода: "Нода".
        labels_dict = {}
        # нода с самым большим количеством стрелок, которые на неё указывают.
        most_arrows = []
        # пополняем информацией из командной анкеты списки и словари, необходимые для визуализации графа.
        for i in range(len(answers_command)):
            # добавляем в список нод, из которых исходят стрелки имя заполнителя командной анкеты.
            arrow_senders.append(answers_command[i][0])
            # добавляем подпись имени оценивающего.
            labels_dict.update({answers_command[i][0]: answers_command[i][0]})
            # в список получателей заносим людей, которых он оценил в ответах на вопросы.
            for x in range(len(answers_command[i])):
                arrow_receivers.append(answers_command[i][x])
                # отдельно создаем связи между заполнителем и всеми, кого он оценил.
                edges_list.append((answers_command[i][0], answers_command[i][x]))
                # добавляем подписи тем, кого он оценил.
                labels_dict.update({answers_command[i][x]: answers_command[i][x]})
        # инициализация графа.
        g = nx.DiGraph()
        # добавляем связи между узлами в граф.
        g.add_edges_from(edges_list)
        # создаём список всех нод, из которого мы уберем моду.
        no_mode_nodes = arrow_receivers + arrow_senders
        try:
            # находим моду нод.
            most_arrows.append(mode(arrow_receivers))
            # находим количество модной ноды в списке.
            val = no_mode_nodes.count(most_arrows[0])
            # удаляем из списка всех нод моду.
            for i in range(val):
                no_mode_nodes.remove(most_arrows[0])
        except Exception:
            # если моды нет, то просто очищаем список.
            most_arrows.clear()
        # определяем положение нод на графе.
        pos = nx.spring_layout(g)
        # проверяем наличие моды нод.
        if most_arrows != []:
            # визуализируем моду нод.
            nx.draw_networkx_nodes(g, pos, nodelist=most_arrows, with_labels=True, node_size=2000, node_color="blue",
                                   font_size=8, font_color="black", horizontalalignment="center")
        # визуализируем все остальные ноды.
        nx.draw_networkx_nodes(g, pos, nodelist=no_mode_nodes, with_labels=True, node_size=2000, node_color="yellow",
                               font_size=8, font_color="black", horizontalalignment="center")
        # визуализируем связи между нодами.
        nx.draw_networkx_edges(g, pos, edgelist=edges_list, edge_vmin=500, with_labels=True, node_size=2000)
        # подписываем названия нод (Вадим, Андрей, Максим)
        nx.draw_networkx_labels(g, pos, nodelist=edges_list, with_labels=True, node_size=2000, font_size=8,
                                font_color="black", horizontalalignment="center")
        # сохраняем в папке со скриптом граф.
        # plt.show() -- показать
        plt.savefig(os.path.join(app.root_path + '/static/graphs/', 'graph_{}_{}.png'.format(str(team_id), str(date)))) #+ str(team_id) + "_" + str(date) + ".png")
                    #format(url_for('static', filename='graphs/'), team_id, str(date)))


# Forms_and_graphs.private_form(name="Максим", questions_private=["Как?", "Где?", "Что?"],
#                    answers_private=["Саня", "Ксения", "Валера"])
# Forms_and_graphs.command_form(questions_command=["Как?", "Где?", "Что?"],
#                    answers_command=[["Максим", "Влад", "Влад", "Андрей"], ["Влад", "Максим", "Фёдор", "Фёдор"],
#                                     ["Фёдор", "Влад", "Максим", "Максим"], ["Андрей", "Влад", "Влад", "Максим"]], team_id=1, date=1)