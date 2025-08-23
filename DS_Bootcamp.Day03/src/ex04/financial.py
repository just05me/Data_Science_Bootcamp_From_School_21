#!/usr/bin/env python3

import sys
import requests
import time
from bs4 import BeautifulSoup

def get_data(ticker: str, field: str):
    url = f"https://finance.yahoo.com/quote/{ticker}/financials"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'  
    }

    respon = requests.get(url, headers=headers)

    if respon.status_code != 200:
        raise Exception(f"Failed with {respon.status_code}")

    sup = BeautifulSoup(respon.text, "html.parser")

    row = sup.find_all("div", {"class": "row lv-0 yf-t22klz"})

    if row:

        for r in row:
            fileName = r.find('div', {'class': 'rowTitle yf-t22klz'})
            
            if fileName:
                if fileName.get("title") == field:

                    col = r.find_all('div', {'class': 'column yf-t22klz'})
                    val = [cl.text.strip() for cl in col]

                    return tuple([field] + val)
    
    else:
        raise Exception(f"Data not found")

if __name__ == "__main__":
    little = sys.argv

    if len(little) != 3:
        raise Exception("Должно быть - ./financial.py \"TICKER\" \"FIELD\"")

    ticker = little[1]
    field = little[2]

    try:
        res = get_data(ticker, field)
        print(res)
    except Exception as e:
        print(e)


# Генерация файлов

# Профилирование с time.sleep(5)
# python -m cProfile -s tottime financial.py "MSFT" "Total Revenue" > profiling-sleep.txt   -Ю  создает profiling-sleep.txt
"""
команда запускает профилирование Python-скрипта financial.py с помощью модуля cProfile и сохраняет результаты
Запускает встроенный модуль профилирования Python
Время выполнения каждой функции
Количество вызовов
Время на вызов

-s tottime
Параметр сортировки результатов
"""

# Профилирование без time.sleep(5)
# python -m cProfile -s tottime financial.py "MSFT" "Total Revenue" > profiling-tottime.txt   -Ю  создает profiling-tottime.txt

# Профилирование с оптимизированным HTTP-клиентом
# python -m cProfile -s tottime financial_enhanced.py "MSFT" "Total Revenue" > profiling-http.txt   -Ю  создает сprofiling-http.txt

# Профилирование по числу вызовов (ncalls)
# python -m cProfile -s ncalls financial_enhanced.py "MSFT" "Total Revenue" > profiling-ncalls.txt   -Ю  создает profiling-ncalls.txt