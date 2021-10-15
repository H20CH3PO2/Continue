class Task:
    start = -1
    # Время начала в часах с 1 января 2010 год с 0:00. Дату и время начала отсчета можно менять.
    # Главное - чтобы все времена были натуральными числами

    finish = -1
    # Время конца в часах с 1 января 2010 год с 0:00.
    # Как и старт - дату и время начала отсчета можно менять.

    cost = -1
    # Цена сдвига данной задачи. В нашем случае для задачи - 1 рубль, для вехи - 1000 рублей

    tasks_before_me = []
    # Список задач, которые идут "раньше нас в графе"

    start_fact = -1
    # Время фактического начала

    dur = -1
    # Длительность задачи

    def __init__(self, start, finish, cost, dur):
        self.start = start
        self.finish = finish
        self.cost = cost
        self.tasks_before_me = []
        self.dur = dur


tasks_dict = []
tasks = []
to_0 = []
to_back = []


def parse_time(day, time):  # Переводим время в удобный дня нас формат
    result = day * 24 + time
    return result


def read_versh(f_versh):  # Читаем вершины
    global tasks
    global to_0
    global to_back
    tasks_dict = dict()
    # В первой строке - кол-во задач + вех(всего вершин графа N)
    # Далее N строк:
    # если веха, то число 1 + id задачи + срок в формате (номер дня с 2010 года) + пробел + (время в часах с 0:00)
    # если задача: число 0 + id задачи + срок начала(номер дня с 1 января 2010 года) + пробел + (время в часах с 0:00) + длительность в часах.
    # Затем такая же информация про конец. Итого 6 чисел.
    # Пример
    # 2
    # 1 37 500 12
    # 0 38 450 12 460 11 40
    # Интерпретация:
    # Есть веха, имеет id 37, срок сдачи - 500ый день считая с 1 января 2010 года; первое января 2010 года имеет номер 0) в 12:00.
    # 2 строка:
    # есть задача, имеет id 38, начало - 450 день с 1 янв 2010 года, в 12:00; конец 460 день в 11:00, длительность 40 часов
    text = f_versh.readlines()
    n = int(str(text[0]))
    for i in range(n):
        b = list(map(int, (text[i + 1]).split()))
        if b[0] == 1:
            time_start = parse_time(b[2], b[3])
            time_finish = time_start
            cost = 1000
            task = Task(time_start, time_finish, cost, 0)
            tasks_dict.update({b[1]: task})
        else:
            time_start = parse_time(b[2], b[3])
            time_finish = parse_time(b[4], b[5])
            cost = 1
            task = Task(time_start, time_finish, cost, b[6])
            tasks_dict.update({b[1]: task})

    # Перенумеруем задачи так, чтобы их нумерация шла с 0 подряд,
    # а также - словари для перехода от одной нумерации к другой
    timer = 0
    to_0 = dict()
    to_back = dict()
    for i in tasks_dict:
        to_0[i] = timer
        to_back[timer] = int(i)
        tasks.append(tasks_dict[i])
        timer += 1


def read_rebs(f_rebs):  # Считываем ребра
    global tasks  # Используем глобальную переменную внутри функции
    global to_0
    global to_back
    # Первая строка содержит 1 число M (кол-во ребер-cвязей).
    # Затем идут M строк, в каждой по 3 числа:
    #  1) номер вершины, откуда ребро исходит
    #  2) номер вершины, куда ребро приходит
    #  3)тип связи между ними
    #   3.1) 1, если окончание-начало + лаг
    #   3.2) 2, если начало-начало + лаг
    #   3.3) 3, если окончание-окончание + лаг
    #   3.4) 4, если начало-окончание + лаг
    # Пример
    # 4 5
    # 1 2 3
    # 1 3 2
    # 1 4 1
    # 2 3 2
    # 2 4 3
    # Что было:
    # 4 задачи, 5 связей. 1->2 начало-начало + лаг, 1->3 окончание-окончание + лаг и т.д. про 1->4 2->3 2->4
    text = f_rebs.readlines()
    m = int(((text[0]).split())[1])
    for i in range(1, m):
        a1, b1, t = list(map(int, (text[i]).split()))
        a = to_0[a1]
        b = to_0[b1]
        tmp = [a, t]
        tasks[b].tasks_before_me.append(tmp)


def read_extra(f_extra):  # Считываем вершину
    global tasks
    global to_0
    global to_back
    # в первой строке вводится номер
    # во второй 2 числа - новый день начала, новое время начала, через пробел
    # пример
    # 2
    # 470 22
    # интерпретация программой. Задачу 2 удалось начать в день 470 в 22:00
    text = f_extra.readlines()
    it = int(text[0]) # считали номер этой задачи
    d, t = map(int, (text[1]).split()) # считали номер дня и время фактического начала
    n_time = parse_time(d, t) # привели к нужному формату время
    it = to_0[str(it)]
    tasks[it].start_fact = n_time


def read_data():  # считываем данные
    f_versh = open('app/Parser/input_tasks.txt', 'r')
    read_versh(f_versh)
    f_rebs = open('app/Parser/input_rebs.txt', 'r')
    read_rebs(f_rebs)
    # f_extra = open('app/Parser/extra.txt', 'r')
    # read_extra(f_extra)

    f_versh.close()
    f_rebs.close()
    # f_extra.close()


top_sort = []  # массив, в котором хранятся вершины в порядке топологической сортировки
used = []  # вспомогательный массив для алгоритма топологической сортировки


def dfs_top_sort(v):  # стандартный алгоритм топологической сортировки, реализованый без использования рекурсии
    global used
    global tasks
    global top_sort
    cash = [v]
    used[cash[-1]] = True
    while len(cash) > 0:
        ok = 1
        for e in tasks[cash[-1]].tasks_before_me:
            if not used[e[0]]:
                cash.append(e[0])
                used[e[0]] = True
                ok = 0

        if ok == 1:
            top_sort.append(cash[-1])
            cash.pop()


def top_sort_graph():  # функция, которая отсортирует наш граф в порядке топологичесокой сортировки
    global used
    global tasks
    for i in range(len(tasks)):
        used.append(False)
    for i in range(len(tasks)):
        if not used[i]:
            dfs_top_sort(i)


straf = 0  # переменная, отвечающая за цену минимального сдвига


def count_mistakes():  # считаем минимальные убытки от сдвига одной задачи
    global straf
    global tasks
    global top_sort
    for i in top_sort:
        if tasks[i].start_fact != -1:
            continue
        able_to_start = tasks[i].start
        for prev_pair in tasks[i].tasks_before_me:
            prev_versh = prev_pair[0]
            type = prev_pair[1]
            if type == 1:
                fact_finish = tasks[prev_versh].start_fact + tasks[prev_versh].dur

                if able_to_start < fact_finish:
                    able_to_start = fact_finish
            elif type == 2:
                if able_to_start < tasks[prev_versh].start_fact:
                    able_to_start = tasks[prev_versh].start_fact
            # type == 3 и type == 4 не накладывают ограничений минимальное время старта, а лишь ограничивают его сверху.
        if able_to_start + tasks[i].dur > tasks[i].finish:
            straf += tasks[i].cost
        tasks[i].start_fact = able_to_start


def print_result():  # выводим результат работы
    global straf
    global tasks
    cnt = 0
    straf_tasks = []
    for i in tasks:
        if i.start_fact + i.dur > i.finish:
            straf_tasks.append((to_back[cnt], i.start_fact + i.dur, i.finish, i.cost))
        cnt += 1
    return straf, straf_tasks
    # выводит информацию о просроченных задачах: id из изначальных данных, конец в оптимальной сортировке,
    # конец по "документам", цену за просрочку данной задачи


def get_result():
    read_data()
    top_sort_graph()
    count_mistakes()
    return print_result()
