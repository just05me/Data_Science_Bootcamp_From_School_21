#!/bin/sh

# Проверяем - передан ли аргумент
if [ -z '$1' ]; then
    exit 1
fi

# Сохраняем аргументы в переменную
VACANCY="$1"

# curl пелает запрос к API hh.ru и получает список вакансий
# Заменяет пробелы на %20 для правильного URL
SEARCH=$(echo "$VACANCY" | sed 's/ /%20/g')

# Качает JSON с сайта hh.ru и сохраняет его во временный файл
# Используем -s для подавления вывода прогресса
curl -s "https://api.hh.ru/vacancies?text=$SEARCH&per_page=20" > temp.json

# Форматиреут JSON и сохраняем его в файл hh.json
jq . temp.json > hh.json
 
# Удаляет временный файл
rm temp.json