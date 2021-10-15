from datetime import datetime

from app import app
from flask import render_template
import threading
import pandas as pd

from app.Parser.Parse_EXEL_file import parse_excel_file, month_list, D1
from app.Parser.algorithm import get_result


parsed = True


def is_parse():
    global parsed
    if not parsed:
        parse_excel_file()
        parsed = True


def recovery_date(days):
    d1 = str(D1.split(' ')[0]) + '-' + str(month_list[str(D1.split(' ')[1])]) + '-' + str(D1.split(' ')[2])
    d1 = datetime.strptime(d1, "%d-%m-%Y").timestamp() * 1000
    d2 = days*60*60*1000 + d1
    return datetime.fromtimestamp(d2/1000).strftime("%d.%m.%Y")


def get_tasks(straf_tasks):
    print(straf_tasks)
    df = pd.read_csv(r'app/Parser/OC2021_IT_Data_ASE.csv')
    tasks = []
    for task in straf_tasks:
        id, rec_end, _, _ = task
        tasks.append({
            'id': id,
            'start': df[df['ID'] == id].iloc[0]['Начало'],
            'end': df[df['ID'] == id].iloc[0]['Окончание'],
            'rec_end': recovery_date(rec_end)
        })
    return tasks


@app.route("/")
@app.route("/main")
def main():
    if not parsed:
        t = threading.Thread(target=is_parse())
        t.start()
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Wait</title>
        </head>
        <body>
            <p>Подаждите 5-7 минут и обновите страницу</p>
        </body>
        </html>
        '''
    else:
        straf, straf_tasks = get_result()

        return render_template('main.html', file={'fine': straf, 'data': get_tasks(straf_tasks)})
