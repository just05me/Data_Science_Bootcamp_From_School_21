#!/bin/sh

# Сохраняем путь к файлу hh.json
INPUT_FILE="../ex00/hh.json"

# Имя выходного файла
OUTPUT_FILE="hh.csv"

# Указывает файл с фильтром для jq
FILTER_FILE="filter.jq"

# Записываем заголовки в CSV файл
echo "\"id\",\"created_at\",\"name\",\"has_test\",\"alternate_url\"" > $OUTPUT_FILE

# Запускает jq с фильтром и сохраняет результат в CSV файл
# Использует -r для вывода в формате CSV
# Использует -f для указания файла с фильтром
jq -r -f $FILTER_FILE $INPUT_FILE >> $OUTPUT_FILE