#!/usr/bin/env python3

import os

if __name__ == "__main__":
    try:
        # Получает путь к вертуал бокс
        venv = os.environ.get("VIRTUAL_ENV")

        if venv:
            print(f"Your current virtual env is {venv}")
        else:
            raise Exception("You are not in a virtual environment.")

    except Exception as e:
        print(e)