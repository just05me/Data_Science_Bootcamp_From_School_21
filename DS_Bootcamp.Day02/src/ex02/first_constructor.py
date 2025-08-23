import sys
import os

class Reserch:
    def __init__(self, file_name):
        self.file_name = file_name

    def file_reader(self):

        if not os.path.exists(self.file_name):
            raise FileNotFoundError(f"Not such file or directory: '{self.file_name}'")
        
        with open(self.file_name, "r") as file:
            res = file.readlines()

        if len(res) < 2:
            raise ValueError(f"File should have 'head' / 'tail' and one or more lines after that that contain either 0 or 1")

        if "head" in res[0].lower() and "tail" in res[0].lower():
            return res

if __name__ == "__main__":
    little = sys.argv

    if len(little) != 2:
        raise ValueError("File name not provided")
    
    try:
        file_name = little[1]
        research = Reserch(file_name)
        file_content = research.file_reader()

        for i in file_content:
            print(i.strip())
            
    except Exception as some:
        print(some)