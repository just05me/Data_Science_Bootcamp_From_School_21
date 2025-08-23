def data_types():
    a = 1
    b = "Hello World"
    c = 1.5
    d = False
    e = [1, 2, 3, 4]
    f = {"name": "Me"}
    g = (1, 2, 3, 4)
    h = {1, 2, 3, 4}

    # Тут вывод получается таким - ['int', 'str', 'float', 'bool', 'list', 'dict', 'tuple', 'set']
    # all_types = [type(a).__name__, type(b).__name__, type(c).__name__, type(d).__name__, type(e).__name__, type(f).__name__, type(g).__name__, type(h).__name__]

    # print(all_types)

    # Тут таким - [int, str, float, bool, list, dict, tuple, set]
    all_types = [type(a).__name__, type(b).__name__, type(c).__name__, type(d).__name__, type(e).__name__, type(f).__name__, type(g).__name__, type(h).__name__]

    return all_types


def main(tip: list):
    print("[", end="")
    print(*tip,sep=", ",end="")
    print("]")


if __name__ == "__main__":
    main(data_types())