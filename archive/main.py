# -*- coding: utf-8 -*-

import requests, time
from bs4 import BeautifulSoup
import re
import json
import datetime
import sys
from collections import defaultdict
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import six
import threading, time, schedule, datetime
from threading import Thread
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPDF
from matplotlib.patches import Rectangle

import imgkit
import random, os

# import wkhtmltopdf

# import telebot
# from telebot import apihelper

"""API_Token = '590160358:AAFJ4omKJNtloSzcHpXilOxqFt1aTT7X-Ow'

bot = telebot.TeleBot(API_Token)

apihelper.proxy = {'https': 'socks5://453468945:SxnNvfci@185.211.245.138:1080'}

markup_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
btn_test = telebot.types.KeyboardButton('Test')

markup_menu.add(btn_test)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?", reply_markup=markup_menu)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.message_id, reply_markup=markup_menu)

bot.polling()"""
# start_time = time.time()

# s = requests.get('https://eu.bmstu.ru/')
# s.encoding = 'utf-8'
# b = bs4.BeautifulSoup(s.text, "html.parser")
"""p3 = b.select('.temperature .p3')
pogoda1 = p3[0].getText()
p4 = b.select('.temperature .p4')
pogoda2 = p4[0].getText()
p5 = b.select('.temperature .p5')
pogoda3 = p5[0].getText()
p6 = b.select('.temperature .p6')
pogoda4 = p6[0].getText()
print('Утром :' + pogoda1 + ' ' + pogoda2)
print('Днём :' + pogoda3 + ' ' + pogoda4)
p = b.select('.rSide .description')
pogoda = p[0].getText()
print(pogoda.strip())"""

"""p4 = b.find('ul', class_='shortcuts')
for i in p4.find_all('a', href=True):
    print(i.getText())
print(p4.find_all('a', href=True))

p3 = b.find('li', class_='eu-tree-leaf')
print(p3)
for i in p3.find_all('a', href=True):
    print(i.getText())
#print("--- %s seconds ---" % (time.time() - start_time))"""


def get_html(url):
    response = requests.get(url, timeout=20.)
    response.encoding = 'utf-8'
    return response.text


def dictify(ul):
    result = {}
    for li in ul.find_all("li", recursive=False):
        key = next(li.stripped_strings)
        ul = li.find("ul")
        if ul:
            result[key] = dictify(ul)
        else:
            result[key] = None
    return result


def get_first_page(html):
    d = {}
    # l = []
    uls = html.find('ul', class_='shortcuts')
    for i in uls.find_all('li')[0:2]:
        # l.append(i.find('a').get_text())
        d[i.find('a').get_text()] = i.find('a').get('href')
    return d


def ask_user(l, d):
    print('Вы можете посмотреть вкладку', l[0], ' или', l[1])
    user_ans = int(input())
    if user_ans < 2:
        ans = d[l[user_ans]]
        return ans


"""def get_faculty(html):
    l_faculty = []
    d_faculty = {}

    uls = html.find('ul', class_='eu-tree-root')

    lis_faculty = uls.find('li', class_='eu-tree-closed')
    l_faculty.append(re.sub(r'\s-.*', '', lis_faculty.find('span').get_text()))
    d_faculty[l_faculty[0]] = []

    index = 0
    for i in lis_faculty.next_siblings:
        if i.find('span') != -1:
            index += 1
            l_faculty.append(re.sub(r'\s-.*', '', i.find('span').get_text()))
            d_faculty[l_faculty[index]] = []

    return l_faculty, d_faculty"""


def get_faculty_page(html):
    l_faculty = []
    d_faculty = {}
    d_depart = {}
    d_group = {}

    uls = html.find('ul', class_='eu-tree-root')

    # print(uls.find('span', text = re.compile('АК - Аэрокосмический')).parent)

    lis_faculty = uls.find('li', class_='eu-tree-closed')
    l_faculty.append(re.sub(r'\s-.*', '', lis_faculty.find('span').get_text()))
    d_faculty[l_faculty[0]] = []
    for i in lis_faculty.find_all('li', class_='eu-tree-closed'):
        # print(i.find('span').get_text())
        text1 = re.sub(r'\s-.*', '', i.find('span').get_text())
        d_faculty[l_faculty[0]].append(text1)
        d_depart[text1] = []
        for j in i.find_all('li', class_='eu-tree-leaf'):
            # print(j.a.get_text())
            text2 = j.a.get_text()
            d_depart[text1].append(text2)
            d_group[text2] = j.a.get('href')

    index = 0
    for i in lis_faculty.next_siblings:
        if i.find('span') != -1:
            index += 1
            l_faculty.append(re.sub(r'\s-.*', '', i.find('span').get_text()))
            # print(l_faculty[index])
            d_faculty[l_faculty[index]] = []
            for j in i.find_all('li', class_='eu-tree-closed'):
                # print(j.find('span').get_text())
                text1 = re.sub(r'\s-.*', '', j.find('span').get_text())
                d_faculty[l_faculty[index]].append(text1)
                d_depart[text1] = []
                for k in j.find_all('li', class_='eu-tree-leaf'):
                    # print(k.a.get_text())
                    text2 = k.a.get_text()
                    d_depart[text1].append(text2)
                    d_group[text2] = k.a.get('href')

    return l_faculty, d_faculty, d_depart, d_group
    # print(l_faculty)
    # print(d_faculty)
    # s = 0
    # for i in d_faculty['']:
    #   s += len(d_depart[i])
    #    print(i, '--', len(d_depart[i]))
    # print(s)

    # print(d_depart)

    # print(d_group)


def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                     header_color='#295293', row_colors=['#f1f1f2', 'w'], edge_color='#40466e', marks_color={},
                     row_find_color='#ffffbf', rot=70, col_size=0.075,
                     name_raw=0, bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        print(data.shape[::-1])
        print(size)
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
        now = datetime.datetime.now()
        ax.set_title('Дата: ' + now.strftime("%d-%m-%Y"), loc='left', fontsize=22)
        size1 = fig.get_size_inches() * fig.dpi
        print(size1, fig.dpi)

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, cellLoc='center', **kwargs)

    l = [-1]
    for i in range(data.shape[1]):
        l.append(i)
    mpl_table.auto_set_column_width(l)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    # prop = mpl_table.properties()
    # cells = prop['celld']
    # cell = cells[1, 0]
    # print(prop)
    # cell.set_height(0.01)

    l = []

    test_col_size = mpl_table._cells[0,0].get_height()*4.2

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            if k in [(0, 0), (0, 1), (0, 2)]:
                cell.set_text_props(weight='normal', color='w')
                cell.set_facecolor(header_color)
                cell.set_height(test_col_size)
            else:
                cell.set_text_props(weight='normal', color='w', rotation=rot)
                cell.set_facecolor(header_color)
                cell.set_height(test_col_size)
        else:
            cell.set_facecolor(row_colors[k[0] % len(row_colors)])
            if k[1] in [0, 1, 2]:
                cell.set_text_props(weight='normal', color='black')
            else:
                if k in marks_color:
                    cell.set_text_props(weight='bold', color=marks_color[k])
                else:
                    cell.set_text_props(weight='bold', color='black')
            if name_raw > 0 and k[0] == name_raw:
                cell.set_facecolor(row_find_color)
        #print(k, cell.get_height())
        if k[1] == 0:
            l.append(cell.get_height())
    #print(mpl_table._cells[(0,1)])
    print(sum(l), l)
    #plt.show()
    return ax


def get_marks(html):
    subjects = []

    d_marks = {}

    tables = html.find('table', class_='standart_table progress_students vertical_hover table-group')

    for i in tables.find('thead').find_all('th'):
        text = i.get_text().strip()
        if len(text) > 40:
            a = re.search(r'[\w\s\d]{18}', text)
            b = re.search(r'\(.*\n*.*', text)
            c = a.group(0) + b.group(0)
            subjects.append(c.replace('(', '\n(').replace(') ', ')\n'))
        else:
            subjects.append(i.get_text().strip().replace('...', '').replace('(', '\n(').replace(') ', ')\n'))

    # print(subjects)

    # num_of_students = int(tables.find('tbody').find_all('tr')[-1].find('td').get_text())

    # matrix_table_marks = np.zeros((num_of_students, len(subjects)))

    # matrix_table_marks[0] = subjects
    # print(matrix_table_marks)

    p = re.compile(r"(?<=color:)#?\w*\d*", re.S | re.I)

    df = pd.DataFrame(columns=subjects)  # , index=range(num_of_students))

    for index, i in enumerate(tables.find('tbody').find_all('tr')):
        l_student = []
        for index_j, j in enumerate(i.find_all('td')):
            if j.find('span', class_='fio_com'):
                l_student.append(j.find('span', class_='fio_com').get_text().replace('\xa0', ' ').replace(' ', '\n'))
            elif j.find('span', class_='p_all'):
                l_student.append(j.find('span', class_='p_all').get_text().strip())
                if j.find('span', class_='p_all').find('span', style=True):
                    d_marks[(index + 1, index_j)] = \
                    p.findall(j.find('span', class_='p_all').find('span', style=True)['style'])[0]
            else:
                l_student.append(j.get_text().strip())

        df.loc[index + 1] = l_student

    # print(d_marks)

    ds = '1'  # Номер студента в группе, надо выбрать
    index = 0
    if ds in list(df[df.columns[0]]):
        index = list(df[df.columns[0]]).index(ds) + 1
    else:
        print('Нет такого номера в группе')

    x = df.shape[0]

    #y = 0.0001123283*(x**3) + 0.0036508693*(x**2) - 0.2660637453*x + 5.2623005477

    y = 5.4356142867*x**(-0.2793620271)

    print(y)

    ax = render_mpl_table(df, col_width=2.4, row_height=y, font_size=22, name_raw=index, marks_color=d_marks)
    fig = ax.get_figure()
    fig.subplots_adjust(0, 0.2, 1, 0.8)
    start = time.time()
    fig.savefig('test.pdf')
    end = time.time()
    print(end - start, ' - время выполнения сохранения pdf')


def get_marks_session(html):
    subjects = []

    d_color = {}

    tables = html.find('table', class_='eu-table sortable-table')

    for i in tables.find('thead').find_all('th'):
        text = i.get_text().strip().replace('/ ', '/').replace(' ', '\n').replace('\xa0', '\n')
        subjects.append(text)

    # print(subjects)

    df = pd.DataFrame(columns=subjects)

    p = re.compile(r"(?<=color:)#?\w*\d*", re.S | re.I)

    for index, i in enumerate(tables.find('tbody').find_all('tr')):
        l_student = []
        for index_j, j in enumerate(i.find_all('td')):
            j.find('del').extract()
            if j.find('div', class_='student-fio'):
                l_student.append(j.find('span').get_text().replace(' ', '\n'))
            else:
                l_student.append(j.get_text().strip())
                if j.get_text().strip() in ['Нзч', 'Я', 'Неуд']:
                    d_color[(index + 1, index_j)] = '#a50026'
                elif j.get_text().strip() == 'Отл':
                    d_color[(index + 1, index_j)] = '#006837'
                elif j.get_text().strip() == 'Хор':
                    d_color[(index + 1, index_j)] = '#66bd63'
                elif j.get_text().strip() == 'Удов':
                    d_color[(index + 1, index_j)] = '#fdae61'
                    # #006837 - green A
                    # #a50026 - red
                    # #fdae61 - orange C
                    # #66bd63 - green B
                # if j.find("span", style=True):
                #    if len(p.findall(j.find("span", style=True)['style'])) != 0:
                #        d_color[(index+1, index_j)] = p.findall(j.find("span", style=True)['style'])[0]

        df.loc[index + 1] = l_student

    # print(d_color)
    ds = '2'  # Номер студента в группе, надо выбрать
    index = 0
    if ds in list(df[df.columns[0]]):
        index = list(df[df.columns[0]]).index(ds) + 1
    else:
        print('Нет такого номера в группе')

    ax = render_mpl_table(df, col_width=5.0, row_height=2.0, font_size=22, name_raw=index, marks_color=d_color,
                          rot=0, col_size=0.02)
    fig = ax.get_figure()
    fig.subplots_adjust(0.2, 0.03, 0.8, 0.97)
    start = time.time()
    fig.savefig('test_session.pdf')
    end = time.time()
    print(end - start, ' - время выполнения сохранения pdf')


def main():
    print('Hello123')
    # group_page_orig
    # faculty_page_guimc
    # group_page_asp
    # group_page_kamil_orig
    # 0.005305152363975894
    with open("faculty_page_guimc.html", encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'lxml')
    start = time.time()
    get_marks(soup)
    end = time.time()
    print(end-start)


# >>>>>>>>>>>>>>>>>>>>>>>>>> Тест Паралельеных потоков >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# <<<<<<<<<<<<<<<<<<<<<<<<<< Тест Паралельеных потоков <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# >>>>>>>>>>>>>>>>>>>>>>>>>> Рабочая версия >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
"""    print('Введи 1 - тек усп, 2 - сессия')

    n = int(input())

    start_time_parse = time.time()

    url = 'https://eu.bmstu.ru'

    start_time = time.time()
    try:
        html = get_html('https://eu.bmstu.ru/')  # исключение по таймауту 20 сек
    except requests.exceptions.Timeout:
        print('Timeout')
    except requests.exceptions.ConnectionError:                       # исключение по битому url
        print('no connection')

    soup = BeautifulSoup(html, 'lxml')
    end_time = time.time()
    print(end_time - start_time, ' - время обращения к https://eu.bmstu.ru/', '\n')
    d_first = get_first_page(soup)
    #print(d_first)

    start_time = time.time()
    html = get_html(url+d_first[' Текущая успеваемость'])

    soup = BeautifulSoup(html, 'lxml')
    end_time = time.time()
    print(end_time - start_time, ' - время обращения к https://eu.bmstu.ru/(тек усп или сессия)', '\n')

    l_f, d_f, d_d, d_g = get_faculty_page(soup)

    json.dump(l_f, open("list_faculty.txt", "w"), ensure_ascii=False)
    l1 = json.loads(open("list_faculty.txt").read())
    #print(l1)

    json.dump(d_f, open("dict_faculty.txt", "w"), ensure_ascii=False)  # этот блок положить в функцию update
    d1 = json.loads(open("dict_faculty.txt").read())
    #print(d1)

    json.dump(d_d, open("dict_departament.txt", "w"), ensure_ascii=False)
    d2 = json.loads(open("dict_departament.txt").read())
    #print(d2)

    if n == 2:
        for i in d_g.keys():
            d_g[i] = d_g[i].replace('progress3', 'session')

    json.dump(d_g, open("dict_group.txt", "w"), ensure_ascii=False)
    d3 = json.loads(open("dict_group.txt").read())

    end_time_parse = time.time()
    print(end_time_parse - start_time_parse, ' - время сбора данных и сохранения в словари', '\n')

    choice = ['Э', 'Э4', 'Э4-83Б']

    #print(d1[choice[0]])

    #print(d2[choice[1]])

    #print(d3[choice[2]])

    start_time = time.time()

    start_site = time.time()

    html = get_html(url + d3[choice[2]])

    soup = BeautifulSoup(html, 'lxml')

    end_site = time.time()
    print(end_site - start_site, ' - время обращения к сайту группы', '\n')

    if n == 1:
        get_marks(soup)
    elif n == 2:
        get_marks_session(soup)

    end_time = time.time()

    print(end_time - start_time, ' - время обработки и сохранения в pdf', '\n')"""
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Рабочая версия <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


if __name__ == '__main__':
    main()

# >>>>>>>>>>>>>>>>>>>>>>>>>> Тест Паралельеных потоков >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

"""def func1():
    url = 'https://eu.bmstu.ru'

    while True:

        #start = time.time()
        #while True:
        #    True
        start = time.time()
        lock.acquire()
        l1 = json.loads(open("list_faculty.txt").read())
        d1 = json.loads(open("dict_faculty.txt").read())
        d2 = json.loads(open("dict_departament.txt").read())
        d3 = json.loads(open("dict_group.txt").read())
        lock.release()
        end = time.time()
        print(end - start)
        print(l1)
        print('choose your faculty:')
        s = input()
        print(s)
        if s in d1.keys():
            if len(d1[s]) == 0:
                print('There is no departaments in your faculty')
                continue
            print(list(d1[s]))
            print('choose your departament:')
            s = input()
            if s in d2.keys():
                print(list(d2[s]))
                print('choose your group:')
                s = input()
                if s in d3.keys():
                    s1 = int(input('1 - тек усп. 2 - сессия\n'))
                    if s1 == 1:
                        url_g = d3[s]
                    elif s1 == 2:
                        url_g = d3[s].replace('progress3', 'session')
                    print(url_g)
                    try:
                        html = get_html(url+url_g)  # исключение по таймауту 20 сек
                    except requests.exceptions.Timeout:
                        print('Timeout')
                    except requests.exceptions.ConnectionError:  # исключение по битому url
                        print('no connection')
                    except Exception:
                        print('Something wrong')
                    else:
                        start = time.time()
                        soup = BeautifulSoup(html, 'lxml')
                        if s1 == 1:
                            get_marks(soup)
                        elif s1 == 2:
                            get_marks_session(soup)
                        end = time.time()
        print(end-start, 'время выполнения get_marks')
        #if s != 'exit':
        #    print('main func worked ', s)
        #else:
        #    break


def func2(done_time):
    while not done_time.wait(5):
        schedule.run_pending()


def job():
    now = datetime.datetime.now()
    t = now.strftime("%H-%M-%S")

    start = time.time()

    try:
        html = get_html('https://eu.bmstu.ru/modules/progress3/')  # исключение по таймауту 20 сек
    except requests.exceptions.Timeout:
        print('Timeout')
    except requests.exceptions.ConnectionError:  # исключение по битому url
        print('no connection')
    except Exception:
        print('Something wrong')
    else:
        soup = BeautifulSoup(html, 'lxml')

    #with open("faculty_page_orig.html", encoding='utf-8') as fp:
    #    soup = BeautifulSoup(fp, 'lxml')

        l_f, d_f, d_d, d_g = get_faculty_page(soup)

        lock.acquire()
        json.dump(l_f, open("list_faculty.txt", "w"), ensure_ascii=False)
        #l1 = json.loads(open("list_faculty.txt").read())
        # print(l1)

        json.dump(d_f, open("dict_faculty.txt", "w"), ensure_ascii=False)  # этот блок положить в функцию update
        #d1 = json.loads(open("dict_faculty.txt").read())
        # print(d1)

        json.dump(d_d, open("dict_departament.txt", "w"), ensure_ascii=False)
        #d2 = json.loads(open("dict_departament.txt").read())
        # print(d2)

        json.dump(d_g, open("dict_group.txt", "w"), ensure_ascii=False)
        #d3 = json.loads(open("dict_group.txt").read())
        lock.release()
        end = time.time()
        print(end - start, ' время выполнения обновления данных')
        print('i upgraded data', ' at ', t)


schedule.every(1).minutes.do(job)

if __name__ == '__main__':
    # a = Thread(target = func1)
    lock = threading.Lock()
    done = threading.Event()
    b = Thread(target=func2, args=[done])
    b.setDaemon(True)
    # a.start()
    b.start()
    # a.join()
    func1()
    done.set()
    # b.join()"""

# <<<<<<<<<<<<<<<<<<<<<<<<<< Тест Паралельеных потоков <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
