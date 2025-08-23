import timeit
import sys

def withloop():
    ll = ["john@gmail.com", "james@gmail.com", "alice@yahoo.com", "anna@live.com", "philipp@gmail.com"]

    res = []

    for i in ll:
        if ".com" in i:
            res.append(i)

def withoutloop():
    ll = ["john@gmail.com", "james@gmail.com", "alice@yahoo.com", "anna@live.com", "philipp@gmail.com"]

    res = [em for em in ll if ".com" in em]

def withmap():
    ll = ["john@gmail.com", "james@gmail.com", "alice@yahoo.com", "anna@live.com", "philipp@gmail.com"]

    res = list(map(lambda em: em if ".com" in em else None, ll))

def filterit():
    ll = ["john@gmail.com", "james@gmail.com", "alice@yahoo.com", "anna@live.com", "philipp@gmail.com"]

    res = list(filter(lambda em: em.endswith(".com"), ll))

if __name__ == "__main__":
    little = sys.argv

    if len(little) == 3:
        if little[1] == "loop":
            with1 = timeit.timeit(withloop, number = int(little[2]))
            print(with1)
        elif little[1] == "list_comprehension":
            with2 = timeit.timeit(withoutloop, number = int(little[2]))
            print(with2)
        elif little[1] == "map":
            with3 = timeit.timeit(withmap, number = int(little[2]))
            print(with3)
        elif little[1] == "filter":
            with4 = timeit.timeit(filterit, number = int(little[2]))
            print(with4)
    else:
        pass