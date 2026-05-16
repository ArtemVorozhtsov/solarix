import pandas as pd
import numpy as np
import datetime as dt
from flask import Flask, render_template, request, redirect, url_for
from bokeh.plotting import figure
from bokeh.embed import components
import os

app = Flask(__name__)

CSV_LOG = 'log.csv'
CSV_FILLING = 'He_filling.csv'

he_level_mapping = {
    100: 970,
    95: 955,
    90: 933,
    85: 907,
    80: 875,
    75: 838,
    70: 795,
    65: 751,
    60: 706,
    55: 654,
    50: 600,
    45: 551
}

def percent_to_liters(percent):
    # Находим ближайшие известные значения
    known_percents = sorted(he_level_mapping.keys())
    lower = max(p for p in known_percents if p <= percent)
    upper = min(p for p in known_percents if p >= percent)
    
    # Линейная интерполяция
    if lower == upper:
        return he_level_mapping[lower]
    else:
        return he_level_mapping[lower] + (he_level_mapping[upper] - he_level_mapping[lower]) * (percent - lower) / (upper - lower)

# Инициализация CSV файлов
for file in [CSV_LOG, CSV_FILLING]:
    if not os.path.exists(file):
        pd.DataFrame(columns=['Date', 'T1', 'T2', 'He_level']).to_csv(file, index=False, sep=';')
        pd.DataFrame(columns=['Date', 'He_level']).to_csv(CSV_FILLING, index=False, sep=';')

# Функция прогноза
def predict_helium_drop(log_df, start_date, start_level):
    log_df = log_df.dropna()
    if len(log_df) < 2:
        return None

    def extrapolate(start_date, start_He):
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        p1 = np.poly1d([np.float64(-0.15026324142223393), 0])
        xx = np.linspace(0, 365, 365)
        prediction = start_He + p1(xx)
        res = next(x for x, val in enumerate(prediction) if val < 55)
        print(start_date, type(start_date))
        return start_date + dt.timedelta(days=res)

    try:
        return extrapolate(start_date, start_level).strftime('%Y-%m-%d')
    except Exception as e:
        print(e)
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем данные из формы
        date_str = request.form['time']  # предполагается, что это строка в каком-то формате
        t1 = float(request.form['T1'])
        t2 = float(request.form['T2'])
        he_level = float(request.form['He'])

        # Преобразуем дату в нужный формат
        try:
            # Сначала пытаемся распарсить дату (адаптируйте под ваш входной формат)
            # Пример для формата '2024-08-28T12:25'
            dt = pd.to_datetime(date_str)
            # Форматируем в нужный вид '2024-08-20 00:00:00'
            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            # Если не получается распарсить, оставляем как есть (или обработайте ошибку)
            formatted_date = date_str

        # Читаем и обновляем лог
        log_df = pd.read_csv(CSV_LOG, sep=';')
        log_df = log_df._append({
            'Date': formatted_date,
            'T1': t1,
            'T2': t2,
            'He_level': he_level
        }, ignore_index=True)
        log_df = log_df.sort_values(by='Date')
        log_df.to_csv(CSV_LOG, index=False, sep=';')

        if 'new_He' in request.form:
            filling_df = pd.read_csv(CSV_FILLING, sep=';')
            filling_df = filling_df._append({
                'Date': formatted_date,
                'He_level': he_level
            }, ignore_index=True)
            filling_df.to_csv(CSV_FILLING, index=False, sep=';')

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/graphs')
def graphs():
    log_df = pd.read_csv(CSV_LOG, sep=';', parse_dates=['Date'])
    log_df = log_df.sort_values(by='Date')
    filling_df = pd.read_csv(CSV_FILLING, sep=';', parse_dates=['Date'])

    if not filling_df.empty:
        last_fill_date = filling_df.iloc[-1]['Date']
        last_fill_level = filling_df.iloc[-1]['He_level']
        prediction = predict_helium_drop(log_df, last_fill_date, last_fill_level)
    else:
        prediction = None

    plots = generate_bokeh_plots(log_df)
    return render_template('graphs.html', plots=plots, prediction=prediction)

def generate_bokeh_plots(df):
    df = df.dropna()
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%dT%H:%M')
    
    # Создаем инструменты для всех графиков
    tools = "pan,wheel_zoom,box_zoom,reset,save"
    
    # График T1
    p1 = figure(title='T1 Temperature', x_axis_label='Date', y_axis_label='T1', 
               x_axis_type="datetime", tools=tools, width=500, height=300)
    p1.line(df['Date'], df['T1'], legend_label='T1', color='blue', line_width=2)
    p1.legend.location = "top_left"
    
    # График T2
    p2 = figure(title='T2 Temperature', x_axis_label='Date', y_axis_label='T2',
               x_axis_type="datetime", tools=tools, width=500, height=300)
    p2.line(df['Date'], df['T2'], legend_label='T2', color='green', line_width=2)
    
    # График He Level
    p3 = figure(title='He Level', x_axis_label='Date', y_axis_label='He Level',
               x_axis_type="datetime", tools=tools,  width=500, height=300)
    p3.line(df['Date'], df['He_level'], legend_label='He Level', color='red', line_width=2)

    df['He_liters'] = df['He_level'].apply(percent_to_liters)
    p4 = figure(title='He Level (Liters)', x_axis_label='Date', y_axis_label='He Volume (L)',
           x_axis_type="datetime", tools=tools,  width=500, height=300)
    p4.line(df['Date'], df['He_liters'], legend_label='He Volume', color='blue', line_width=2)
    
    # Генерируем компоненты
    script, (div1, div2, div3, div4) = components([p1, p2, p3, p4])
    
    return {
        'script': script,
        'div': {
            'plot1': div1,
            'plot2': div2,
            'plot3': div3,
            'plot4': div4
        }
    }

@app.route('/table')
def table():
    log_df = pd.read_csv(CSV_LOG, sep=';', parse_dates=['Date'], date_format='mixed')
    return render_template('table.html', log_df=log_df)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
