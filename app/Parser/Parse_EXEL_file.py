import pandas as pd
from datetime import datetime
import numpy as np


D1 = '01 Январь 2010 00:00' #Дата, от которой отсчитываем дни


#Создание класса "задача"
class task(object):
    def __init__(self, id: str, followers: str, predecessor: str):
        self.id = id
        self.followers = followers
        self.predecessor = predecessor


#Функция для подсчета кол-ва дней между 2 датами
def days_between(d1: str, d2: str):
    '''Counts the number of days between 2 dates'''
    
    month_list = {'Январь': 1, 'Февраль': 2, 'Март': 3, 'Апрель': 4, 'Май': 5, 'Июнь': 5,
                  'Июль': 7, 'Август': 8, 'Сентябрь': 9, 'Октябрь': 10, 'Ноябрь': 11, 'Декабрь': 12}
    d1 = str(d1.split(' ')[0]) + '-' + str(month_list[str(d1.split(' ')[1])]) + '-' + str(d1.split(' ')[2])
    d2 = str(d2.split(' ')[0]) + '-' + str(month_list[str(d2.split(' ')[1])]) + '-' + str(d2.split(' ')[2])
    d1 = datetime.strptime(d1, "%d-%m-%Y")
    d2 = datetime.strptime(d2, "%d-%m-%Y")
    
    return abs((d2 - d1).days)


#Функция парсинга файла с удалением пустых строк
def parse_exel_to_csv(exelfile: pd.DataFrame, csv_filename=r'OC2021_IT_Data_ASE.csv'):
    '''Parses the file and removes blank lines'''
    
    indexes_to_drop = []
    for i in range(exelfile.shape[0]):
        if pd.isna(exelfile.iloc[i]['Последователи']) and pd.isna(exelfile.iloc[i]['Предшественники']):
            indexes_to_drop.append(i)
    indexes_to_keep = set(range(exelfile.shape[0])) - set(indexes_to_drop)
    df_sliced = exelfile.take(list(indexes_to_keep))
    df_sliced.to_csv(csv_filename, index=False, header=True)
    print('File converted!')
    
    return 0


#Функция, оставляющая только ID в задачах-наследниках/предшественниках
def keep_only_id(task: task):
    '''Keep only numbers in AI followers and predecessors'''
    
    #Убраем буквы в последователях
    followers = task.followers.split(';')
    followers_clear = []
    for follower in followers:
        followers_clear.append(splitting_task(follower)[0])

    # Убраем буквы в предшественниках
    predecessors = task.predecessor.split(';')
    predecessors_clear = []
    for predecessor in predecessors:
        predecessors_clear.append(splitting_task(predecessor)[0])

    #Получаем конечные значения последователя и предшественника без букв
    task.followers = ';'.join(followers_clear)
    task.predecessor = ';'.join(predecessors_clear)
    
    return task


#Функция поиска и добавления недостающих связей в любой из 2х задач на входе
#Логика: смотрим в наследник 1й задачи и ищем в нем 2ю задачу. Если находим ее, то проверяем, есть ли в предшественниках
#2й задачи 1я. Если нет - добавляем. По аналогии для других комбинаций наследника и предшественника
def add_branches_for_2_tasks(task1: task, task2: task):
    '''Supplements 2 tasks with missing links'''

    #Очищаем последователей и предшественников от букв
    task1_cleared = keep_only_id(task1)
    task2_cleared = keep_only_id(task2)

    #Создаем списки из последователей и предшественников
    followers1 = task1_cleared.followers.split(';')
    predecessors1 = task1_cleared.predecessor.split(';')
    followers2 = task2_cleared.followers.split(';')
    predecessors2 = task2_cleared.predecessor.split(';')

    #Проверяем вхождения ID одной задачи в последователи/предшественники
    #и ID другой задачи в предшественники/последователи (4 случая)
    if task1.id in followers2:
        if not(task2.id in predecessors1):
            if task1.predecessor == '':
                task1.predecessor += task2.id
            else:
                task1.predecessor += ';' + task2.id

    if task2.id in followers1:
        if not(task1.id in predecessors2):
            if task2.predecessor == '':
                task2.predecessor += task1.id
            else:
                task2.predecessor += ';' + task1.id

    if task1.id in predecessors2:
        if not(task2.id in followers1):
            if task1.followers == '':
                task1.followers = task2.id
            else:
                task1.followers += ';' + task2.id

    if task2.id in predecessors1:
        if not(task1.id in followers2):
            if task2.followers == '':
                task2.followers += task1.id
            else:
                task2.followers += ';' + task1.id

    return task1, task2


#Функция добавления связей для конкретных задач. Происходит путем перебора всех задач из файла: каждая задача
#проверяется на наличие связей с конкретной задачей.
def add_branches_for_tasks(csv_file: pd.DataFrame, indexes):
    '''Supplements tasks from the list ID with missing links'''
    
    addition_array = [] #Список с обьектами ["задача", index задачи]

    #Добавление связей в tasks по id
    for i in indexes:
        id1 = str(csv_file.loc[i, 'ID'])
        followers1 = str(csv_file.iloc[i]['Последователи'])
        predecessors1 = str(csv_file.loc[i]['Предшественники'])
        task1 = task(id1, followers1, predecessors1)
        for j in range(csv_file.shape[0]):
            id2 = str(csv_file.iloc[j]['ID'])
            followers2 = str(csv_file.iloc[j]['Последователи'])
            predecessors2 = str(csv_file.iloc[j]['Предшественники'])
            task2 = task(id2, followers2, predecessors2)
            task1 = add_branches_for_2_tasks(task1, task2)[0]
            addition_array.append([task1, i])
            
    #Записть в файл полученных значений
    for one_task in addition_array:
        help_task = one_task[0]
        csv_file.at[one_task[1], 'Последователи'] = help_task.followers
        csv_file.at[one_task[1], 'Предшественники'] = help_task.predecessor

    return 0


#Функция добавления связей для всех задач. Аналогична функции add_branches_for_tasks, но проверяет связи каждой задачи с
#каждой. Алгоритмическая сложность O(n^2)
def add_branches_for_all_tasks(csv_file: pd.DataFrame):
    '''Complements all tasks with missing links'''
    
    for i in range(csv_file.shape[0]):

        #Создаем обьект task1
        id1 = str(csv_file.iloc[i]['ID'])
        followers1 = str(csv_file.iloc[i]['Последователи'])
        predecessors1 = str(csv_file.iloc[i]['Предшественники'])
        task1 = task(id1, followers1, predecessors1)

        for j in range(csv_file.shape[0] - i):
            # Создаем обьект task2
            id2 = str(csv_file.iloc[j]['ID'])
            followers2 = str(csv_file.iloc[j]['Последователи'])
            predecessors2 = str(csv_file.iloc[j]['Предшественники'])
            task2 = task(id2, followers2, predecessors2)

            #Добавляем недостающие ребра
            task1, task2 = add_branches_for_2_tasks(task1, task2)

            #Записываем результат
            csv_file.at[j, 'Последователи'] = task2.followers
            csv_file.at[j, 'Предшественники'] = task2.predecessor
        csv_file.at[i, 'Последователи'] = task1.followers
        csv_file.at[i, 'Предшественники'] = task1.predecessor

    return 0


#Функция, считающая количество связей для "задача->последователь"
#Суммируются все последователи и предшественники всех задач, после чего сумма делится на 2 (Сумма степеней вершин графа
#равна удвоенному числу его ребер)
def branch_count(csv_file: pd.DataFrame):
    '''Counts the number of links in the task list'''
    count = 0
    #2 Равносильные реализации, т.к. после добавления всех недостающих связей, кол-во связей последователей =  кол-во
    #связей предшественников
    #
    #for i in range(csv_file.shape[0]):
    #    for j in range(len(str((csv_file.iloc[i]['Последователи'])).split(';'))):
    #        if not(pd.isna(csv_file.iloc[i]['Последователи'])):
    #            count += 1
    
    for i in range(csv_file.shape[0]):
        if not(pd.isna(csv_file.iloc[i]['Последователи'])):
            count += len(str((csv_file.iloc[i]['Последователи'])).split(';'))
        if not (pd.isna(csv_file.iloc[i]['Предшественники'])):
            count += len(str((csv_file.iloc[i]['Предшественники'])).split(';'))
    return count / 2


#Функция, разделяющая последователя/предка на номер задачи и тип связи
def splitting_task(task: str):
    '''Distributes follower/predecessor to issue number and link type'''
    
    branch_number = {
        'ОН': '1',
        'НН': '2',
        'ОО': '3',
        'НО': '4',
    } #Виды связей
    
    task_type = ''.join(filter(str.isalpha, task))

    #Если в задаче присутствует тип связи
    if task_type != str(np.NaN) and task_type != '':
        task_type = task_type[0:2]
        branch_type_position = tuple(task.find(x) for x in ['ОН', 'НН', 'ОО', 'НО'] if x in task)[0]
        clear_task = task[0: branch_type_position]
    # Если в задаче не присутствует тип связи или задача пустая (np.NaN)
    else:
        task_type = 'ОН'
        clear_task = task

    return clear_task, branch_number[task_type]


#Функция для создания вспомогательного файла input_rebs.txt (описан в algorythm.py)
def create_input_rebs(csv_file: pd.DataFrame, txt_filename=r'app/Parser/input_rebs.txt'):
    '''Create input_rebs.txt'''
    
    txt_file = open(txt_filename, 'w')

    txt_file.write(str(csv_file.shape[0]))
    txt_file.write(' ')
    txt_file.write(str(branch_count(csv_file)) + '\n')

    for i in range(csv_file.shape[0]):
        for j in range(len(str((csv_file.iloc[i]['Последователи'])).split(';'))):
            if not(pd.isna(csv_file.iloc[i]['Последователи'])):
                task_clear,  branch_number = splitting_task(str((csv_file.iloc[i]['Последователи'])).split(';')[j])
                txt_file.write(str(csv_file.iloc[i]['ID']) + ' ')
                txt_file.write(task_clear + ' ')
                txt_file.write(branch_number + '\n')
                
    txt_file.close()
    
    return 0


#Функция для создания вспомогательного файла input_tasks.txt (описан в algorythm.py)
def create_input_tasks(csv_file: pd.DataFrame, txt_filename=r'app/Parser/input_tasks.txt'):
    '''Create input_tasks.txt'''
    
    global D1 
    txt_file = open(txt_filename, 'w')

    txt_file.write(str(csv_file.shape[0]) + '\n')
    for i in range(csv_file.shape[0]):
        if str(csv_file.iloc[i]['Длительность'])[0] == '0':
            #Веха
            txt_file.write('1 ')
            txt_file.write(str(csv_file.iloc[i]['ID']) + ' ')
            txt_file.write(str(days_between(D1, csv_file.iloc[i]['Начало'])) + ' ')
            time_of_milestone = str(csv_file.iloc[i]['Начало']).split(' ')[-1]
            time_of_milestone = time_of_milestone[0: time_of_milestone.find(":")]
            txt_file.write(time_of_milestone + '\n')
        else:
            #Задача
            txt_file.write('0 ')
            txt_file.write(str(csv_file.iloc[i]['ID']) + ' ')
            txt_file.write(str(days_between(D1, csv_file.iloc[i]['Начало'])) + ' ')
            time_of_task = str(csv_file.iloc[i]['Начало']).split(' ')[-1]
            time_of_task = time_of_task[0: time_of_task.find(":")]
            txt_file.write(time_of_task + ' ')

            txt_file.write(str(days_between(D1, csv_file.iloc[i]['Окончание'])) + ' ')
            time_of_task = str(csv_file.iloc[i]['Окончание']).split(' ')[-1]
            time_of_task = time_of_task[0: time_of_task.find(":")]
            txt_file.write(time_of_task + ' ')

            txt_file.write(str(csv_file.iloc[i]['Длительность'])[:-1:] + '\n')
            
    txt_file.close()
    
    return 0


#Функция удаления пустых задач (которые есть в наследниках или в предшественниках, но у которых нет отдельной строки)
def delete_empty_task(csv_file: pd.DataFrame):
    '''Removes tasks that do not have a separate line'''
    
    id_list = [] #список ID со всеми задачами, которые имеют свою строку

    for i in range(csv_file.shape[0]):
        id_list.append(str(csv_file.iloc[i]['ID']))

    #В каждой задаче проверяем списки последователей/предшественников на наличие ID задачи, которая не входит в id_list
    for i in range(csv_file.shape[0]):
        followers = str(csv_file.iloc[i]['Последователи']).split(';')
        for follower in followers:
            if follower != str(np.nan):
                if not (splitting_task(follower)[0] in id_list):
                    followers.remove(follower)
                    csv_file.at[i, 'Последователи'] = ';'.join(followers)

        predecessors = str(csv_file.iloc[i]['Предшественники']).split(';')
        for predecessor in predecessors:
            if predecessor != str(np.nan):
                if not (splitting_task(predecessor)[0] in id_list):
                    predecessors.remove(predecessor)
                    csv_file.at[i, 'Предшественники'] = ';'.join(predecessors)
                    
    csv_file.to_csv(r'app/Parser/OC2021_IT_Data_ASE.csv', index=False, header=True)
    
    return csv_file


#Функция для обнаружения задач, которым нужно дополнить наследников или предшественников, и добавления в них недостающих
#наследников и предшественников
def add_all_missing_branches_in_file(csv_file: pd.DataFrame, csv_filename=r'app/Parser/OC2021_IT_Data_ASE.csv'):
    '''Detects tasks whose predecessors have "..." at the end and complements them'''
    
    incomplete_lists = [] #Список со всеми ID строк, у которых обнаружено "..."

    for i in range(csv_file.shape[0]):
        #Проверяем всех предшественников
        if str(csv_file.iloc[i]['Предшественники']).count('...') != 0:
            string = str(csv_file.iloc[i]['Предшественники'])
            string = string[0: max(string.rfind(k) for k in ";")]
            csv_file.at[i, 'Предшественники'] = string
            incomplete_lists.append(i)
        # Проверяем всех последователей
        if str(csv_file.iloc[i]['Последователи']).count('...') != 0:
            string = str(csv_file.iloc[i]['Последователи'])
            string = string[0: max(string.rfind(k) for k in ";")]
            csv_file.at[i, 'Последователи'] = string
            incomplete_lists.append(i)

    #Добавляем связи по списку
    add_branches_for_tasks(csv_file, incomplete_lists)
    csv_file.to_csv(csv_filename, index=False, header=True)
    
    return csv_file


#Функция, состоящая из функций: add_all_missing_branches_in_file и delete_empty_task
def correct_file(csv_file: pd.DataFrame, filename=r'OC2021_IT_Data_ASE.csv'):
    csv_file = add_all_missing_branches_in_file(csv_file)
    csv_file.to_csv(filename, index=False, header=True)
    csv_file = delete_empty_task(csv_file)
    csv_file.to_csv(filename, index=False, header=True)
    
    return 0


#Функция создания всех вспомогательных файлов
def create_supporting_files(csv_file: pd.DataFrame):
    create_input_rebs(csv_file)
    create_input_tasks(csv_file)
    
    return 0


exelfile = pd.read_excel(r'app/Parser/OC2021_IT_Data_ASE.xlsx', dtype={'ID': int,
                                                            'Начало': str,
                                                            'Длительность': str,
                                                            'Окончание': str,
                                                            'Последователи': str,
                                                            'Предшественники': str})
csv_file = pd.read_csv(r'app/Parser/OC2021_IT_Data_ASE.csv')


#parse_exel_to_csv(exelfile)
#correct_file(csv_file)
#create_supporting_files(csv_file)
