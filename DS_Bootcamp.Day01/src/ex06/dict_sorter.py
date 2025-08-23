def bubble_sort(arr: list):
    for i in range(len(arr)-1, 0, -1):
        swap = False
        for j in range(i):
            if arr[j][0] < arr[j+1][0]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swap = True
            elif arr[j][0] == arr[j+1][0]:
                if arr[j][1] > arr[j+1][1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swap = True
        if not swap:
            return arr
            

def sort_dict(result: dict):
    sorted_tuple = []

    for coun, num in result.items():
        sorted_tuple += [(int(num), coun)]

    return bubble_sort(sorted_tuple)


def tuple_to_dict():
    list_of_tuples = [
    ('Russia', '25'),
    ('France', '132'),
    ('Germany', '132'),
    ('Spain', '178'),
    ('Italy', '162'),
    ('Portugal', '17'),
    ('Finland', '3'),
    ('Hungary', '2'),
    ('The Netherlands', '28'),
    ('The USA', '610'),
    ('The United Kingdom', '95'),
    ('China', '83'),
    ('Iran', '76'),
    ('Turkey', '65'),
    ('Belgium', '34'),
    ('Canada', '28'),
    ('Switzerland', '26'),
    ('Brazil', '25'),
    ('Austria', '14'),
    ('Israel', '12')
    ]

    res = {}

    for i in list_of_tuples:
        res[i[0]] = i[1]

    return res
  

def output(var: list):
    for i in var:
        print(i[1])


def main():
    new_dict = tuple_to_dict()

    sorted_dict = sort_dict(new_dict)

    output(sorted_dict)


if __name__ == "__main__":
    main()