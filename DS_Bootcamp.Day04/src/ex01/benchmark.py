import timeit

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


if __name__ == "__main__":
    with1 = timeit.timeit(withloop, number = 900)
    with2 = timeit.timeit(withoutloop, number = 900)
    with3 = timeit.timeit(withmap, number = 900)
    
    if with1 < with2:
        print("it is better to use a list comprehension")
    elif with2 < with3:
        print("it is better to use a map")
    else:
        print("it is better to use a list loop")
    
    print(f"{with1} vs {with2} vs {with3}")