#!/usr/bin/env python3

import sys
import requests
import time
from bs4 import BeautifulSoup

def get_data(ticker: str, field: str):
    # Это URL чтобы заходить в Yahoo
    # Динамичексий URL
    url = f"https://finance.yahoo.com/quote/{ticker}/financials"

    # Это заголовок который помогает входить в сайт иммитируя действия пользователя
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Отпрвляет Get запрос по url
    # Получает requests.Response Response <Response> object
    response = requests.get(url, headers=headers)

    # Если response.status_code == 200 то страница сайта запущена корректно
    # В ином случае (404, 500, 403) Дается ошибка 
    if response.status_code != 200:
        raise Exception(f"Invalid URL {response.status_code}")

    # Создается HTML парсер который будет парсить html скрипт в response.text
    # Используем встроенный в python парсер "html.parser"
    # С задержкой в исполнение в 5 секунд. Это нужно чтобы случайно не запустить ddos attack и снизить нагрузку на сайт
    sup = BeautifulSoup(response.text, "html.parser")

    time.sleep(5)

    # Тута скрипт ищет все элементы с "div" в которых будет class "row lv-0 yf-t22klz" - Я не знаю как найти это не в ручную
    # rows получает список объектов строк таблиц
    rows = sup.find_all('div', {'class': 'row lv-0 yf-t22klz'})

    if not rows:
        raise Exception("Financial data rows not found")

    # Тута общая логика такая
    # Проходимя по rows и ищем тот который содержит наш Field
    # Нашли идем и извлекаем все остальные элементы с "div" в которых будут доп данные
    # value берет на себя все эти элементы которые содержат текст и в конце преобразует их в tuple и возвращает их
    # value будет таким +- -> ('Total Revenue', '385,706,000', '396,017,000', '394,328,000')
    # В остальных случаях будет ошибка
    for row in rows:
        field_name_div = row.find('div', {'class': 'rowTitle yf-t22klz'})

        if field_name_div and field_name_div.get('title') == field:
            columns = row.find_all('div', {'class': 'column yf-t22klz'})
        
            values = [col.text.strip() for col in columns]
    
            return tuple([field] + values)

    raise Exception("Requested not found")


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