import sys

# Это функция для получения Key from Value
def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k
        

def check_input(val: str):
    if not val:
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

    # Разделил строку по запятым
    split_val = val.split(",")

    # Тут проверяю на лишние запятые. Хз легче способ не нашел
    for n in split_val:
        n = n.replace(" ","")

        if not n:
             return

    # Это уже разбор идет
    for i in split_val:
        i = i.replace(" ","")
        
        if i.capitalize() in COMPANIES:
                print(f"{i.capitalize()} stock price is {STOCKS[COMPANIES[i.capitalize()]]}")
                
        elif i.upper() in STOCKS:
                print(f"{i.upper()} is a ticker symbol for {get_key(COMPANIES, i.upper())}")

        else:
                print(f"{i.capitalize()} is an unknown company or an unknown ticker symbol")
        

def get_input_from_commandLine():
    # Передает параметры с терминала в переменную в виде list
    num = sys.argv

    # Проверяет количество переданных елементов с терминала. num[0] -> названия файла. num[1] -> параметр переданный с названием
    if len(num) == 2:
        return num[1].lower()


def main():
    input_c = get_input_from_commandLine()

    check_input(input_c)


if __name__ == "__main__":
    main()