class Research:
    def file_reader():
        with open("../ex00/data.csv", "r") as file:
            return file.readlines()

if __name__ == "__main__":
    file = Research.file_reader()
    for i in file:
        print(i.strip())