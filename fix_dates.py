import pandas as pd
from datetime import datetime

def fix_dates_in_file(filename):
    """Преобразует даты в файле в формат ISO8601"""
    try:
        # Пробуем прочитать файл с разными вариантами форматов дат
        df = pd.read_csv(filename, sep=';', parse_dates=['Date'], dayfirst=True, date_format='mixed')
        
        # Преобразуем все даты к ISO8601 формату
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%dT%H:%M')
        
        # Сохраняем обратно
        df.to_csv(filename, index=False, sep=';')
        print(f"Файл {filename} успешно обработан")
    except Exception as e:
        print(f"Ошибка при обработке файла {filename}: {str(e)}")

if __name__ == '__main__':
    files = ['log.csv', 'He_filling.csv']  # Укажите ваши файлы
    for file in files:
        fix_dates_in_file(file)