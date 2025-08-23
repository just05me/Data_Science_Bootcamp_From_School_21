import sys
from random import randint

class Research:
    def __init__(self, file_name):
        self.file_name = file_name

    def file_reader(self, has_header = True):
        result = []

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
    def __init__(self, data):
        self.data = data

    def counts(self):
        head, tail = 0, 0

        for i in self.data:
            if i == [1, 0]:
                head += 1
            elif i == [0, 1]:
                tail += 1
        return head, tail        

    def fractions(self, head, tail):
        n1 = (head / (head + tail)) * 100
        n2 = (tail / (head + tail)) * 100

        return n1, n2


class Analytics(Calculations):
    def predict_random(self, number = 3):
        res = []

        for i in range(number):
            ran = randint(0, 1)
            if ran == 1:
                res.append([1, 0])
            elif ran == 0:
                res.append([0, 1])

        return res
    
    def predict_last(self):
        return self.data[-1]



if __name__ == "__main__":
    little = sys.argv

    if len(little) != 2:
        raise ValueError("File name not provided")

    try:
        
        file_name = little[1]

        research = Research(file_name)

        file_content = research.file_reader()

        counters = Calculations(file_content)

        head, tail = counters.counts()
        fract1, fract2 = counters.fractions(head, tail)

        analystic = Analytics(file_content)

        predict = analystic.predict_random()

        last = analystic.predict_last()

        print(file_content)
        print(head, tail)
        print(fract1, fract2)
        print(predict)
        print(last)


    except Exception as some:
        print(some)