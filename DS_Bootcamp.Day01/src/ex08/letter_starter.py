import sys


def input_from_commandLine():
    val = sys.argv

    if len(val) != 2:
        raise Exception("Invalid argument")
    else:
        return val[1]

def get_email(val: str):
    with open("employees.tsv", "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line == '':
            continue

        name, surname, email = line.split('\t')

        if email == val:
            return name
    else:
        raise Exception("Email not found")


def output(name: str):
    print(f"Dear {name}, welcome to our team. We are sure that it will be a pleasure to work with you. That’s a precondition for the professionals that our company hires.")


def main():
    a = input_from_commandLine()
    b = get_email(a)
    output(b)


if __name__ == "__main__":
    main()