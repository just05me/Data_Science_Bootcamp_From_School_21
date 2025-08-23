import timeit
import sys
from functools import reduce

def withloop(a):
    res = 0
    for i in range(1, a + 1):
        res += i * i
    return res

def reduceit(a):
    return reduce(lambda m, i: m + i * i, range(1, a + 1), 0)


if __name__ == "__main__":
    little = sys.argv

    if len(little) == 4:
        if little[1] == "loop":
            with1 = timeit.timeit(lambda: withloop(int(little[3])), number=int(little[2]))
            print(with1)
        elif little[1] == "reduce":
            with2 = timeit.timeit(lambda: reduceit(int(little[3])), number=int(little[2]))
            print(with2)
    else:
        pass