#!/usr/bin/env python3

import os
import subprocess

def main():
    env = os.environ.get("VIRTUAL_ENV")

    if "anibalpe" not in env:
        raise Exception("Ur not in venv")

    # Запускает введеные команда в терминале
    # chek = True - если будет ошибка скрипт ляжет с исключением
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check = True)

    subprocess.run("clear", check = True)

    # И в конце просто печатает все версии в терминал
    subprocess.run(["pip", "freeze"], check = True)

def save_all():
    # Сохраняем все в requirements.txt 
    with open("requirements.txt", "w") as file:
        subprocess.run(['pip', 'freeze'], stdout=file)

if __name__ == "__main__":
    main()
    save_all()

# tar -czf venv_backup.tar.gz anibalpe
# Архивирует окружение в формат tar.gz
# -czf -> c - создает архив, z - сжимает его с gzip, f - сохроняет все с указаным названием