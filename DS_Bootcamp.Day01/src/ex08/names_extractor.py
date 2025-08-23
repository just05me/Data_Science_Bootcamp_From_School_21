import sys

def input_from_commandLine():
    val = sys.argv

    if len(val) != 2:
        raise Exception("Invalid argument")
    else:
        return val[1]

def filter_val(file_path: str):
    res = []

    with open(file_path, 'r') as file:

        for line in file:
            
            if not line.strip():
                continue

            email = line.strip()                        # Очищает str от лишних пробелов и \n
            parts = email.split('@')                    # Делит email по @ на 2 части
            name_surname = parts[0]                     # Передает 1 значения parts - Имя.Фамилия
            name, surname = name_surname.split('.')     # Передает разделенное значение по "." к двум переменным

            # Тут переводят первый символ на верхний регистор
            name = name.capitalize()
            surname = surname.capitalize()

            res.append([name, surname, email])

    return res

def save_val(data: list):
    with open('employees.tsv', 'w') as ffile:
        ffile.write("Name\tSurname\tE-mail\n")
        # Построчно пишет в файл данные
        for name, surname, email in data:
            ffile.write(f"{name}\t{surname}\t{email}\n")


def main():
    a = input_from_commandLine()
    b = filter_val(a)
    save_val(b)


if __name__ == '__main__':
    main()