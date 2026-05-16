import pandas as pd
import sys
import re
from datetime import datetime

def excel_to_csv(input_excel, output_csv):
    # Чтение Excel
    try:
        df = pd.read_excel(input_excel, header=None)
    except Exception as e:
        raise ValueError(f"Ошибка чтения Excel: {e}")

    # Проверка и назначение столбцов
    if len(df.columns) < 2:
        raise ValueError("Файл должен содержать минимум 2 столбца")
    
    df = df.iloc[:, :4]  # Берем первые 4 столбца
    df.columns = ['Date', 'He_level', 'T1', 'T2'][:len(df.columns)]

    # Преобразование данных
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    # if df['Date'].isnull().any():
    #     raise ValueError("Обнаружены некорректные даты")
    
    # Обработка числовых столбцов
    num_cols = ['He_level', 'T1', 'T2']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Сортировка по дате
    df = df.sort_values('Date')

    # Сохранение с помощью pandas (чтобы сохранить типы данных)
    df.to_csv(output_csv, sep=';', index=False, 
             date_format='%Y-%m-%d %H:%M:%S',
             float_format='%.1f',
             na_rep='')

    # Постобработка для точного соответствия формату
    with open(output_csv, 'r+', encoding='utf-8') as f:
        content = f.read()
        content = content.replace('"', '')  # Удаляем кавычки
        f.seek(0)
        f.write(content)
        f.truncate()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python convert.py <input.xlsx> <output.csv>")
        sys.exit(1)

    try:
        excel_to_csv(sys.argv[1], sys.argv[2])
        print(f"Конвертация успешна. Числовые значения сохранены как числа.")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)