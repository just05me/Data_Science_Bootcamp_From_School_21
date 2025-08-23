import os
from random import randint
import logging
from config import file_LOG, TG_webhook, TG_chat_id
import requests

logging.basicConfig(filename=file_LOG,
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')

class Research:
    def __init__(self, fp):
        self.file_path=fp

    def file_reader(self, has_header=True):
        result=[]
        
        logging.info("Read file: %s", self.file_path)

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

        logging.info("Successfully read %d rows", len(result))
        
        return result

    def send_to_telegram(self, message):
        try:
            responce=requests.post(TG_webhook, data={"chat_id": TG_chat_id, 'text': message})
            responce.raise_for_status()
            
            logging.info("Telegram message sent")

        except Exception as e:
            logging.error("Telegram error: %s", e)

class Calculation:
    def __init__(self, data):
        self.data=data

    def counts(self):
        logging.info("Calculating counts")
        head, tail = 0, 0

        for i in self.data:
            if i == [1, 0]:
                head += 1
            elif i == [0, 1]:
                tail += 1
        return head, tail  
    
    def fractions(self,heads,tails):
        logging.info("Calculating fractions")
        n1 = (head / (head + tail)) * 100
        n2 = (tail / (head + tail)) * 100

        return n1, n2

class Analytics(Calculation):
    def predict_random(self, n=3):
        res = []

        for i in range(n):
            ran = randint(0, 2)

            if ran == 1:
                res.append([1, 0])
            elif ran == 0:
                res.append([0, 1])

        return res

    def predict_last(self):
        logging.info("Getting last prediction")

        return self.data[-1:]

    def save_file(self, data,filename,extension):
        logging.info("Saving report to file: %s.%s", filename, extension)

        with open(f"{filename}.{extension}", "w") as file:
            file.write(data)

        logging.info("Report saved")