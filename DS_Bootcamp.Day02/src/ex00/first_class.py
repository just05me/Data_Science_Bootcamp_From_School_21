class Must_read:
    with open("data.csv", "r") as file:
        for i in file:
            print(i.strip())


if __name__ == "__main__":
    Must_read()