#!/usr/bin/env python3

import pytest
import sys
import requests
import time
from bs4 import BeautifulSoup

def get_data(ticker: str, field: str):
    # URL Запрос динамический
    url = f"https://finance.yahoo.com/quote/{ticker}/financials"

    # Заголовок имитирующий работу браузера чтоб yahoo не дала бан
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

    res = get_data(ticker, field)
    print(res)

# Проверка - Запещен pytest в этом интрепритаторе? 
# sys.modules - это словарь. Keys там это работающие модули
if 'pytest' in sys.modules:
    def test_valid_data():
        # Сохраняем данные с get_data 
        result = get_data("MSFT", "Total Revenue")
        # assert - встроенная функция для проверки условий 
        # isinstance - встроенная функция которая проверяет тип данных у переменной
        # assert - ждет ответ от isinstance. isinstance он возвращает в True/False. И так происходит проверка
        assert isinstance(result, tuple)
        assert result[0] == "Total Revenue"

    def test_invalid_ticker():
        # Тут get_data даст ошибку (испключение)
        # pytest.raises - контекстный менеджер который может обрабатывать иснлючения и останавливать тест если такого не будет
        with pytest.raises(Exception):
            get_data("XYZ123", "Total Revenue")

    def test_invalid_field():
        with pytest.raises(Exception):
            get_data("MSFT", "NonExistentField")