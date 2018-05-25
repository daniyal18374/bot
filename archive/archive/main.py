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
import imgkit
import random, os
#import wkhtmltopdf

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
    response = requests.get(url)
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
    l = []
    uls = html.find('ul', class_='shortcuts')
    for i in uls.find_all('li'):
        l.append(i.find('a').get_text())
        d[i.find('a').get_text()] = i.find('a').get('href')
    return l, d


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
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([8, 15])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax

def get_marks(html):

    subjects = []

    tables = html.find('table', class_= 'standart_table progress_students vertical_hover table-group')
    #print(tables)

    for i in tables.find('thead').find_all('th'):
        subjects.append(i.get_text().strip().replace('...', '\n'))

    print(subjects)

    num_of_students = int(tables.find('tbody').find_all('tr')[-1].find('td').get_text())

    #matrix_table_marks = np.zeros((num_of_students, len(subjects)))

    #matrix_table_marks[0] = subjects
    #print(matrix_table_marks)

    df = pd.DataFrame(columns=subjects)#, index=range(num_of_students))

    for index, i in enumerate(tables.find('tbody').find_all('tr')):
        l_student = []
        for j in i.find_all('td'):
            if j.find('span', class_ = 'fio_com'):
                l_student.append(j.find('span', class_ = 'fio_com').get_text().replace('\xa0', ' '))
            elif j.find('span', class_ = 'p_all'):
                l_student.append(j.find('span', class_ = 'p_all').get_text().strip())
            else:
                l_student.append(j.get_text().strip())
        df.loc[index+1] = l_student

    #df.to_csv('df_csv', sep='\t')
    ax = render_mpl_table(df)
    fig = ax.get_figure()
    start = time.time()
    fig.savefig('test.png')
    end = time.time()
    print(end - start)



def main():
    # url = "https://avito.ru/moskva/telefony?p=1&q=htc"
    """with open("first_page_orig.html", encoding='utf-8') as fp:   #вместо этого получение html страницы по запросу
        soup = BeautifulSoup(fp, 'lxml')
    l_from_first_page, d_from_first_page = get_first_page(soup)
    ans_from_first_page = ask_user(l_from_first_page,d_from_first_page)

    if ans_from_first_page == 'https://eu.bmstu.ru/modules/progress3/':  # вместо этого получение html страницы по запросу
        with open("faculty_page_orig.html", encoding='utf-8') as fp:
            soup = BeautifulSoup(fp, 'lxml')                                     ПЕРВАЯ СТРАНИЦА
        get_faculty_page(soup)
    elif ans_from_first_page == 'https://eu.bmstu.ru/modules/session/':
        with open("faculty_page_orig.html", encoding='utf-8') as fp:
            soup = BeautifulSoup(fp, 'lxml')
        print('Вкладка Сессия недоступна')"""
    # При нажатии /start вызывается функция update, которая обновляет словари, также обновить их можно по нажатию кнопки "Обновить данные"
    # После этого пользователь выбирает факультет, кафедру и группу через интеративное меню
    #start_time_site_call = time.time()
    with open("group_page_orig.html", encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'lxml')
     #get_faculty_page(soup)
    """url = 'https://eu.bmstu.ru/modules/progress3/'

    #try:
    html = get_html(url)
    #except:
    #   print('Сайт недоступен')

    soup = BeautifulSoup(html, 'lxml')
    end_time_site_call = time.time()
    #print(html)
    # ---------------------------------------------------------------------------
    start_time = time.time()
    l_f, d_f, d_d, d_g = get_faculty_page(soup)

    json.dump(l_f, open("list_faculty.txt", "w"), ensure_ascii=False)
    l1 = json.loads(open("list_faculty.txt").read())                        СТРАНИЦА ФАКУЛЬТЕТОВ КАФЕДР
    print(l1)

    json.dump(d_f, open("dict_faculty.txt", "w"), ensure_ascii=False)  # этот блок положить в функцию update
    d1 = json.loads(open("dict_faculty.txt").read())
    print(d1)

    json.dump(d_d, open("dict_departament.txt", "w"), ensure_ascii=False)
    d2 = json.loads(open("dict_departament.txt").read())
    print(d2)

    json.dump(d_g, open("dict_group.txt", "w"), ensure_ascii=False)
    d3 = json.loads(open("dict_group.txt").read())

    url_bmstu = 'https://eu.bmstu.ru'

    print(url_bmstu+d3['ИУ6-22М'])
    print(url_bmstu+d3['ИУ6-22М'].replace('progress3', 'session'))
    #https://eu.bmstu.ru/modules/progress3/group/5b3d00a4-203c-11e7-9db8-005056960017/
    #print('https://eu.bmstu.ru'+"/modules/session/group/5b3d00a4-203c-11e7-9db8-005056960017/")"""
    # ---------------------------------------------------------------------------

    now = datetime.datetime.now()
    print(now.strftime("%d-%m-%Y"))

    """print(l_f)
    print('Input your faculty:')
    faculty_name = input()
    if faculty_name in l_f:
        print(d_f[faculty_name])
        print('Input your departament:')
        depart_name = input()
        if depart_name in d_f[faculty_name]:
            print(d_d[depart_name])
            print('Input your group:')
            group_name = input()
            if group_name in d_d[depart_name]:
                print(d_g[group_name])"""
    # print(l, '\n', d)
    #end_time = time.time()
    #print(end_time_site_call - start_time_site_call, ' - время обращения к сайту')
    #print(end_time - start_time, ' - время выполнения функций')
    # print(p)

    start_time = time.time()
    get_marks(soup)
    end_time = time.time()
    print(end_time - start_time, ' - время выполнения функций')
    #print(soup)



if __name__ == '__main__':
    main()
