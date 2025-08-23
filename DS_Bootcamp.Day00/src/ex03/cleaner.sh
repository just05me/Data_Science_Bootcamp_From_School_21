#!/bin/sh

# Указывает входной CSV файл
INPUT_FILE="../ex02/hh_sorted.csv"

# Указывает выходной CSV файл
OUTPUT_FILE="hh_positions.csv"

# Копирует заголовки из входного файла
head -n 1 $INPUT_FILE > $OUTPUT_FILE

# Обрабатывает строки со второй
# Использует tail для получения всех строк кроме первой
# Использует awk для обработки строк
# Использует -F для указания разделителя
tail -n +2 $INPUT_FILE | awk -F '",' '{
# Начальное значение позиции — 
    position = "-"

# Проверяет - есть Junior в имени
    if ($3 ~ /[Jj]unior/) {
        position = "Junior"
    }

# Проверяем - есть Middle в имени
    if ($3 ~ /[Mm]iddle/) {
        if (position == "-") {
            position = "Middle"
        } else {
            position = position "/Middle"
        }
    }

# Проверяет - есть Senior в имени
    if ($3 ~ /[Ss]enior/) {
        if (position == "-") {
            position = "Senior"
        } else {
            position = position "/Senior"
        }
    }

# Формирует новую строку с обновленным именем
# Использует print для вывода строки
# Использует $1 для первого столбца
# Использует $2 для второго столбца
# Использует position для третьего столбца
# Использует $4 для четвертого столбца
    print $1 "\"," $2 "\",\"" position "\"," $4
}' >> $OUTPUT_FILE