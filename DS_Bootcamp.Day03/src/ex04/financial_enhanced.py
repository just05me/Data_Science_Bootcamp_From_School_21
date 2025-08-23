#!/usr/bin/env python3

import sys
import httpx
from bs4 import BeautifulSoup


def fetch_data_httpx(ticker: str, field: str):
    url = f"https://finance.yahoo.com/quote/{ticker}/financials"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  
        "Accept-Language": "en-US,en;q=0.9"
    }

    # HTTP запрос
    # Создается Http клиент и дается запрос
    with httpx.Client() as cl:
        repo = cl.get(url, headers=headers)

        # Печатает URL по которому зашел
        print(f"Request: {repo.url}")

        if repo.status_code != 200:
            raise Exception(f"Failed with: {repo.status_code}")
        
        # repo.text
        # Это html текст с сайта полученый чараз http запрос 
        # И BeautifulSoup парсит по этому скрипту используя встроенный в python парсер "html.parser"
        sup = BeautifulSoup(repo.text, "html.parser")

        # Ишем данные с помощью find_all в sup
        # Ищет все теги <div>
        # С классом row lv-0 yf-t22klz
        row = sup.find_all("div", {"class": "row lv-0 yf-t22klz"})

        if row:
            for r in row:
                # Передаем в fileName первый класс с названием "rowTitle yf-t22klz"
                fileName = r.find('div', {'class': 'rowTitle yf-t22klz'})
                
                if fileName:
                    # Если значение атрибута title будет == field
                    if fileName.get("title") == field:
                        
                        # В col передаем все классы с r с названием "column yf-t22klz"
                        col = r.find_all('div', {'class': 'column yf-t22klz'})
                        # Тута полученый col разбираем по частям
                        # Проходимся по col и берем отрибут text убираем все лишние пробелы
                        val = [cl.text.strip() for cl in col]

                        # Сохраняем результат в tuple и возвращаем
                        return tuple([field] + val)
        
        else:
            raise Exception(f"Field not found {field}")

if __name__ == "__main__":
    little = sys.argv

    if len(little) != 3:
        raise Exception("Должно быть - ./financial.py \"TICKER\" \"FIELD\"")

    ticker = little[1]
    field = little[2]

    try:
        result = fetch_data_httpx(ticker, field)
        print(result)
    except Exception as e:
        print(f"Error: {e}")