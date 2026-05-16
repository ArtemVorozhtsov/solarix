import pandas as pd
import sys

def sort_csv_by_date(input_file):
    # Чтение CSV-файла
    df = pd.read_csv(input_file, sep=';', parse_dates=['Date'])
    
    # Сортировка по дате
    df = df.sort_values(by='Date')
    
    # Перезапись исходного файла
    df.to_csv(input_file, sep=';', index=False, date_format='%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python script.py <input_file.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    sort_csv_by_date(input_file)
    print(f"Файл {input_file} успешно отсортирован по дате.")