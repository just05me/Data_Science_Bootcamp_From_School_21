def read_and_write():
    # Открывать файл для чтения
    with open('ds.csv', 'r') as open_file:
        lines = open_file.readlines()
    
    # Открывать для записи
    with open('ds.tsv', 'w') as w_file:
        
        # Проходимся по строкам 
        for line in lines:
            line = line.rstrip("\n")       # Тут удаляется перенос строки в конце каждой строки. Это не обязательно, но лучше будет чем не будет
            field = []
            current_field = ''             
            quotes = False
            
            i = 0
            
            # Проходиться по каждому элементу в строки и обрабатывает строки. Сохраняет данные с line в field без запятых
            while i < len(line):
                char = line[i]
 
                if char == '"':
                    quotes = not quotes
                    current_field += char

                elif char == ',' and not quotes:
                    field.append(current_field)
                    current_field = ''

                else:
                    current_field += char

                i += 1
            
            field.append(current_field)
            
            # Эта параша пишет в файл строки с field и между елементами ставит пробел через join
            w_file.write('\t'.join(field) + '\n')


if __name__ == '__main__':
    read_and_write()