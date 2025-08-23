import sys 

def get_stock_info(ticker: str):
    if not ticker:
        return

    COMPANIES = {
    'Apple': 'AAPL',
    'Microsoft': 'MSFT',
    'Netflix': 'NFLX',
    'Tesla': 'TSLA',
    'Nokia': 'NOK'
    }

    STOCKS = {
    'AAPL': 287.73,
    'MSFT': 173.79,
    'NFLX': 416.90,
    'TSLA': 724.88,
    'NOK': 3.37
    }

    # Переводит на верхний регистор
    ticker_name = ticker.upper()
    
    # Проверяет есть ли название в dicts и печатает результат    
    if ticker_name in STOCKS:
        for i,j in COMPANIES.items():
            if j == ticker_name:
                print(i, STOCKS[ticker_name])
    else:
        print("Unknown ticker")


def get_input_from_commandLine():
    # Передает параметры с терминала в переменную в виде list
    num = sys.argv

    # Проверяет количество переданных елементов с терминала. num[0] -> названия файла. num[1] -> параметр переданный с названием
    if len(num) == 2:
        return num[1].lower()
    else:
        return None


def main():
    input_f = get_input_from_commandLine()

    get_stock_info(input_f)


if __name__ == "__main__":
    main()