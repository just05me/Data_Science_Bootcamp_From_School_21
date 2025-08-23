import sys
import os

class Research:
    def __init__(self, file_name):
        self.file_name = file_name

    def file_reader(self, has_header = True):
        result = []

        if not os.path.exists(self.file_name):
            raise FileNotFoundError(f"Not such file or directory: '{self.file_name}'")

        with open(self.file_name, "r") as file:
            res = file.readlines()

        if len(res) < 2:
            raise ValueError(f"File should have 'head' / 'tail' and one or more lines after that that contain either 0 or 1")

        if "head" in res[0].lower() and "tail" in res[0].lower():
            has_header = True
        else:
            raise ValueError(f"File should have 'head' / 'tail' and one or more lines after that that contain either 0 or 1")

        for i in range(1, len(res)):
            strings = res[i].strip()
            num1, num2 = strings.split(",") 
            result.append([int(num1), int(num2)])

        return result


class Calculations:
    def counts(self, data):
        head, tail = 0, 0

        for i in data:
            if i == [1, 0]:
                head += 1
            elif i == [0, 1]:
                tail += 1
        return head, tail        

    def fractions(self, head, tail):
        n1 = (head / (head + tail)) * 100
        n2 = (tail / (head + tail)) * 100

        return n1, n2



if __name__ == "__main__":
    little = sys.argv

    if len(little) != 2:
        raise ValueError("File name not provided")

    try:
        file_name = little[1]

        research = Research(file_name)
    
        counters = Calculations()
    
        file_content = research.file_reader()
    
        head, tail = counters.counts(file_content)
    
        fract1, fract2 = counters.fractions(head, tail)

        print(file_content)
        print(head, tail)
        print(fract1, fract2)

    except Exception as some:
        print(some)