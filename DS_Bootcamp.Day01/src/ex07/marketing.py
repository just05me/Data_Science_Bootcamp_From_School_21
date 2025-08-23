import sys


def get_call_center_emails(val1, val2, val3):
    return (set(val1) | set(val2)) - set(val3)

def get_potential_clients(val1, val2, val3):
    return set(val2) - set(val1) - set(val3)

def get_loyalty_program_emails(val1, val2, val3):
    return (set(val1) | set(val1)) - set(val2)

def input_from_commandLine():
    names = [
    "call_center",
    "potential_clients",
    "loyalty_program"
    ]
    
    val = sys.argv

    if len(val) == 2 and val[1] in names:
        return val[1]
    else:
        raise Exception("Invalid argument")



def business_solution(val):
    clients = [
    'andrew@gmail.com', 
    'jessica@gmail.com', 
    'ted@mosby.com',
    'john@snow.is', 
    'bill_gates@live.com', 
    'mark@facebook.com',
    'elon@paypal.com', 
    'jessica@gmail.com'
    ]

    participants = [
    'walter@heisenberg.com', 
    'vasily@mail.ru',
    'pinkman@yo.org',
    'jessica@gmail.com', 
    'elon@paypal.com',
    'pinkman@yo.org', 
    'mr@robot.gov', 
    'eleven@yahoo.com'
    ]
    
    recipients = [
    'andrew@gmail.com', 
    'jessica@gmail.com', 
    'john@snow.is'
    ]

    if val == "call_center":
        return get_call_center_emails(clients, participants, recipients)
    elif val == "potential_clients":
        return get_potential_clients(clients, participants, recipients)
    elif val == "loyalty_program":
        return get_loyalty_program_emails(clients, participants, recipients)


def output(var):
    for i in var:
        print(i)


def main():
    input_c = input_from_commandLine()

    output_c = business_solution(input_c)

    output(output_c)


if __name__ == "__main__":
    main()