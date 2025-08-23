import os
from random import randint

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
    def predict_random(self, number):
        res = []

        for i in range(number):
            ran = randint(0, 2)
            
            if ran == 1:
                res.append([1, 0])
            elif ran == 0:
                res.append([0, 1])

        return res
    
    def predict_last(self):
        return self.data[-1]
    
    def save_file(self, data, file_name, ext):
        with open(f"{file_name}.{ext}", "a") as file:
            file.write(data)