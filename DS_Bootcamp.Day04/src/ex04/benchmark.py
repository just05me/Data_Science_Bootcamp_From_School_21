import timeit
import random
from collections import Counter

def manCount(data):
    res = {}
    for i in data:
        if i in res:
            res[i] += 1
        else:
            res[i] = 1

    return res

def top10(data):
    res = sorted(
        data.items(),           # Берет данные с dict и переводит их в tuple
        key = lambda x: x[1],   # Тут сортируется по 2 значение
        reverse=True            # По убыванию? Да (True)
    )

    return res[:10]             # Возвращаются первые 10 


if __name__ == "__main__":
    some = [random.randint(0, 100) for i in range(1000000)]

    with1 = timeit.timeit(lambda: manCount(some), number=1)
    with2 = timeit.timeit(lambda: Counter(some), number=1)
    
    c1 = manCount(some)
    c2 = Counter(some)
    
    top1 = timeit.timeit(lambda: top10(c1), number=1)
    top2 = timeit.timeit(lambda: c2.most_common(10), number=1)

    print(f"my function: {with1}")
    print(f"Counter: {with2}")
    print(f"my top: {top1}")
    print(f"Counter's top: {top2}")