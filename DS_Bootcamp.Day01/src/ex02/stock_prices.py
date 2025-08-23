import sys 

def get_stock_price(company: str):

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

    if not company:
        return
    
    # Переводит первую букву на верхний регистор
    company_name = company.capitalize()
    
    # Проверяет есть ли название в dicts и печатает результат    
    if company_name in COMPANIES:
        print(STOCKS[COMPANIES[company_name]])
    else:
        print("Unknown company")

def get_input_from_commandLine():
    # Передает параметры с терминала в переменную в виде list
    num = sys.argv

    # Проверяет количество переданных елементов с терминала. num[0] -> названия файла. num[1] -> параметр переданный с названием
    if len(num) == 2:
        return num[1].lower()


def main():
    input_f = get_input_from_commandLine()

    get_stock_price(input_f)


if __name__ == "__main__":
    main()