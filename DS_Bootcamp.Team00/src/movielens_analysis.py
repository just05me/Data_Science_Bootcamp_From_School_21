import os
import requests
from bs4 import BeautifulSoup
import json
import pytest
from collections import defaultdict, OrderedDict, Counter
import datetime
import re
import time


"""
Функции для статистических вычислений
-------------------------------------------------------------------------
"""

# Вычисляет среднее значение.
def calculate_mean(data: list):
    return sum(data) / len(data) if data else 0

# Вычисляет медиану.
def calculate_median(data: list):
    if not data:
        return 0

    sorted_data = sorted(data)
    mid = len(sorted_data) // 2

    return (sorted_data[mid - 1] + sorted_data[mid]) / 2 if len(sorted_data) % 2 == 0 else sorted_data[mid]

# Вычисляет дисперсию.
def calculate_variance(data: list):
    if len(data) < 2:
        return 0

    mean_value = calculate_mean(data)
    
    return sum((x - mean_value) ** 2 for x in data) / (len(data) - 1)

"""
Классы для обработки данных
Основная логика
-------------------------------------------------------------------------
"""

# Класс для определения рейтинга
class Ratings:
    def __init__(self, path):
        # Словарь для хранения названий фильмов по ID
        self.movie_titles = {}

        # Словари для группировки рейтингов по фильмам и пользователям
        self.ratings_by_movie = defaultdict(list)
        self.ratings_by_user = defaultdict(list)

        # Определяем путь к файлу movies.csv
        dir = path.rfind('/')

        # Проверяет файл в этой директории? Так она может адаптироваться под ситуацию
        if dir == -1:
            movies_path = 'movies.csv'  # Same directory if no '/'
        else:
            movies_path = path[:dir] + '/movies.csv'
        
        try:
            # Читаем файл и расшифроем его. Для сопостовления названия и ID
            with open(movies_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                header = lines[0].strip()

                for line in lines:
                    line = line.strip()

                    if not line:
                        continue

                    parts = line.split(',')

                    if len(parts) < 3:
                        continue

                    movie_id = parts[0]

                    title = ','.join(parts[1:-1])
                    genres = parts[-1]
                    self.movie_titles[movie_id] = title

        except FileNotFoundError:
            raise FileNotFoundError(f"File {movies_path} not found.")
        
        except IOError as e:
            raise IOError(f"Error reading {movies_path}: {e}")

        try:
            # Читаем файл и расшифроем его. для сбора данных о рейтингах
            with open(path, 'r', encoding='utf-8') as f:
                # Пропускаем заголовок
                header=next(f)

                for line in f:
                    line = line.strip()
                
                    if not line:
                        continue

                    parts = line.split(',')
                
                    if len(parts) < 4:
                        continue
                
                    user_id = parts[0]
                    movie_id = parts[1]
                
                    try:
                        rating = float(parts[2])
                        timestamp = int(parts[3])

                        # Сохраняем рейтинги по фильмам и пользователям
                        self.ratings_by_movie[movie_id].append((user_id, rating, timestamp))
                        self.ratings_by_user[user_id].append((movie_id, rating, timestamp))

                    except ValueError:
                        continue
        except FileNotFoundError:
            raise FileNotFoundError(f"File {path} not found.")
    
        except IOError as e:
            raise IOError(f"Error reading {path}: {e}")
        
        # Инициализируем подклассы для анализа фильмов и пользователей
        self.movies = self.Movies(self)
        self.users = self.Users(self)

    # Подкласс для анализа рейтингов фильмов
    class Movies:
        def __init__(self, data):
            # Ссылка на основной объект Ratings
            self.data = data

        # Распределение рейтингов по годам
        def dist_by_year(self): 
            counts = defaultdict(int)

            for movie_id, ratings in self.data.ratings_by_movie.items():
                for i in ratings:

                    timestamp = i[2]

                    try:

                        # Преобразуем timestamp в дату
                        date = datetime.datetime.fromtimestamp(timestamp)
                        year = date.year
                        counts[year] += 1

                    except ValueError or OSError:
                        continue

            # Сортируем по году
            rating_by_year = sorted(counts.items(), key=lambda x: x[0])
            
            # Возвращаем отсортированный картедж как словарь
            return dict(rating_by_year)
        
        # Распределение рейтингов по значениям
        def dist_by_rating(self):
            counts = defaultdict(int)

            for movie_id, ratings in self.data.ratings_by_movie.items():
                for rating_tuple in ratings:

                    rating_val = rating_tuple[1]
                    counts[rating_val] += 1
            
            # Сортируем по значению рейтинга
            ratings_distribution = sorted(counts.items(), key=lambda x: x[0])
            
            # Возвращаем отсортированный картедж как словарь
            return dict(ratings_distribution)
        
        # Топ-N фильмов по количеству рейтингов
        def top_by_num_of_ratings(self, n):
            movie_count = {}

            for movie_id, ratings in self.data.ratings_by_movie.items():
            
                count = len(ratings)
                title = self.data.movie_titles.get(movie_id, 'Unknown')
                movie_count[title] = count
            
            # Сортируем по значению рейтинга
            top_movies = sorted(movie_count.items(), key=lambda x: x[1], reverse=True)[:n]
            
            # Возвращаем отсортированный картедж как словарь
            return dict(top_movies)
        
        # Топ-N фильмов по среднему или медианному рейтингу
        def top_by_ratings(self, n, metric='average'):
            movie_rating = {}

            for movie_id, ratings in self.data.ratings_by_movie.items():
            
                rating_list = [rate[1] for rate in ratings]
            
                if len(rating_list) == 0:
                    score = 0.0
                else:
                    if metric == 'median':
                        score = calculate_median(rating_list)
                    else:
                        score = calculate_mean(rating_list)
                
                # Округляем до 2 знаков
                score = round(score, 2)
                title = self.data.movie_titles.get(movie_id, 'Unknown')
                movie_rating[title] = score
            
            # Сортируем по убыванию
            top_movies = sorted(movie_rating.items(), key=lambda x: x[1], reverse=True)[:n]
            
            # Возвращаем отсортированный картедж как словарь
            return dict(top_movies)
        
        # Топ-N фильмов по дисперсии рейтингов
        def top_controversial(self, n):
            movie_var = {}
            
            for movie_id, ratings in self.data.ratings_by_movie.items():
            
                rating_list = [rate[1] for rate in ratings]
            
                if len(rating_list) == 0:
                    variance = 0.0
                else:
                    variance = calculate_variance(rating_list)
            
                # Округляем до 2 знаков
                variance = round(variance, 2)
                title = self.data.movie_titles.get(movie_id, 'Unknown')
                movie_var[title] = variance
            
            top_movies = sorted(movie_var.items(), key=lambda x: x[1], reverse=True)[:n]  # Сортируем по убыванию
            
            return dict(top_movies)

    # Подкласс для анализа рейтингов пользователей
    class Users(Movies):
        def __init__(self, data):
            
            # Наследуем от Movies
            super().__init__(data)

        # Распределение пользователей по количеству выставленных рейтингов
        def dist_by_num_of_ratings(self):
            user_ratings = defaultdict(int)
            
            for user_id, ratings in self.data.ratings_by_user.items():
                num_ratings = len(ratings)
                user_ratings[num_ratings] +=1
            
            # Сортируем по количеству
            rating_by_user = sorted(user_ratings.items(), key=lambda x: x[0])
            
            return dict(rating_by_user)
        
        # Распределение пользователей по среднему или медианному рейтингу
        def dist_by_metric(self, metric='average'):
            user_ratings = defaultdict(int)
            
            for user_id, ratings in self.data.ratings_by_user.items():
                rating_list = [rate[1] for rate in ratings]
            
                if len(rating_list) == 0:
                    value = 0.0
                else:
                    if metric == 'median':
                        value = calculate_median(rating_list)
                    else:
                        value = calculate_mean(rating_list)
                
                # Округляем до 2 знаков
                value = round(value, 2)
                user_ratings[value] += 1
            
            # Сортируем по значению
            top_ratings = sorted(user_ratings.items(), key=lambda x: x[0])
            
            return dict(top_ratings)
        
        # Топ-N пользователей по дисперсии рейтингов
        def top_controversial(self, n):
            user_var = {}
            
            for user_id, ratings in self.data.ratings_by_user.items():
                rating_list = [rate[1] for rate in ratings]
            
                if len(rating_list) == 0:
                    var = 0.0
                else:
                    var = calculate_variance(rating_list)
                
                # Округляем до 2 знаков
                var = round(var, 2)  
                user_var[user_id] = var
            
            # Сортируем по убыванию
            top_ratings = sorted(user_var.items(), key=lambda x: x[1], reverse=True)[:n]
            
            return dict(top_ratings)

# Для анализа тегов из датасета MovieLens
class Tags:
    def __init__(self, path):

        # Списки для хранения всех тегов + уникальных тегов
        # Для отслеживания их частоты
        self.tags = []

        # Для уникальных елементов ускорить поиск
        self.unique_tags = set() # avoid duplcates

        try:
            # Читаем файл и расшифроем его. Для сбора тегов.
            with open(path, 'r', encoding='utf-8') as f:

                # Пропускаем заголовок
                next(f)

                for line in f:
                    line = line.strip()
                    tokens = line.split(',')
                
                    if len(tokens) <4:
                        continue
                    
                    # Берет срез от третьего элемента до предпоследнего Уичтывая запятые
                    tag = ','.join(tokens[2:-1]).strip()

                    # Добавляем тег в список всех тегов
                    self.tags.append(tag)

                    # Добавляем тег в множество уникальных тегов
                    self.unique_tags.add(tag)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {path} not found.")
        
        except IOError as e:
            raise IOError(f"Error reading {path}: {e}")

    # Топ-N тегов по количеству слов
    def most_words(self, n):
        tag_counts = {}

        for tag in self.unique_tags:

            # Считаем слова в теге
            count = len(tag.split())
            tag_counts[tag]=count
        
        # Сортируем по убыванию слов и алфавиту
        big_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
        
        return dict(big_tags[:n])

    # Топ-N самых длинных тегов по символам
    def longest(self, n):
        tags = [(tag, len(tag)) for tag in self.unique_tags]

        # Сортируем по убыванию длины и алфавиту
        big_tags = sorted(tags, key=lambda x: (-x[1], x[0]))
        
        return [tag for tag, _ in big_tags[:n]]

    # Топ-N тегов, которые одновременно имеют много слов и большую длину
    def most_words_and_longest(self, n):
        # Создаем множество топ-N тегов по количеству слов
        # Сортируем по убыванию слов и алфавиту
        top_by_words = set(tag for tag, _ in sorted([(tag, len(tag.split())) for tag in self.unique_tags], key=lambda x: (-x[1], x[0]))[:n])
        
        # Получаем множество топ-N тегов по длине
        top_by_length = set(self.longest(n))
        
        # Возвращаем отсортированные пересечение двух множеств
        return sorted(top_by_words & top_by_length)
        
    # Топ-N самых популярных тегов
    def most_popular(self, n):
        counts = defaultdict(int)

        for tag in self.tags:
            counts[tag] +=1
        # Сортируем по - по убыванию количества появлений - по алфавиту для тегов с одинаковой частотой 
        popular_tags = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        
        return dict(popular_tags[:n])
        
    # Функция для поиска тегов
    def tags_with(self, word):
        # Перевод на нижний регистор для корректной работы
        lower = word.lower()

        # Создаем список тегов в которых есть искомое слово
        # Проверяем на регистор 
        tags_with_word = [tag for tag in self.unique_tags if lower in tag.lower()]
        
        return sorted(tags_with_word)

# Класс для анализа метаданных из movies.csv датасета MovieLens
class Movies:
    def __init__(self, path):
        self.movies = []

        try:
            # Читаем файл и расшифроем его. Для сбора тегов.
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Сохраняем заголовок
                header = lines[0].strip()
            
                # Перебираем строки с 2 строки
                for line in lines[1:]:
                    line = line.strip()
            
                    if not line:
                        continue
            
                    parts = line.split(',')
            
                    if len(parts) < 3:
                        continue
            
                    movie_id = parts[0]
                    genres = parts[-1]

                    # Извлекаем название объединяя все между movieId и genres
                    title = ','.join(parts[1:-1]).strip()

                    year = None

                    # Ищем год использую регулярное выражение
                    year_match = re.search(r'\((\d{4})\)$', title)
            
                    if year_match:
                        year = year_match.group(1)
                    
                    # Добавляем dict с данными в list
                    self.movies.append({
                        'movie_id': movie_id,
                        'title': title,
                        'genres': genres,
                        'year': year
                    })
        except FileNotFoundError:
            raise FileNotFoundError(f"File {path} not found.")
        
        except IOError as e:
            raise IOError(f"Error reading {path}: {e}")

    # Функция для распределения фильмов по годам выпуска
    def dist_by_release(self):
        count = defaultdict(int)

        for movie in self.movies:
            if movie['year']:
                count[movie['year']] +=1
        
        # Сортируем по убыванию количества фильмов + по алфавиту с одинаковым количеством
        release_years = sorted(count.items(), key=lambda x: (-x[1], x[0]))
        
        # Преобразуем список в OrderedDict для сохранения порядка сортировки
        return OrderedDict(release_years)
    
    # Функция распределения фильмов по жанрам
    def dist_by_genres(self):
        count = defaultdict(int)

        for movie in self.movies:
            # Проверка есть жанры?
            if movie['genres'] != '(no genres listed)':
                
                for genre in movie['genres'].split('|'):
                    count[genre] += 1
        
        # Сортируем по убыванию количества фильмов + по алфавиту с одинаковым количеством
        genres = sorted(count.items(), key=lambda x: (-x[1], x[0]))
        
        # Преобразуем список в OrderedDict для сохранения порядка сортировки
        return OrderedDict(genres)
        
    # Топ-N фильмов с наибольшим количеством жанров
    def most_genres(self, n):
        genre_count = []

        for movie in self.movies:
        
            if movie['genres'] == '(no genres listed)':
                count = 0
            else:
                count = len(movie['genres'].split('|'))
        
            # Добавляем название + количество жанров в list
            genre_count.append((movie['title'], count))
        
        # Сортируем по убыванию количества жанров + по алфавиту с одинаковым количеством жанров
        movies = sorted(genre_count, key=lambda x: (-x[1], x[0]))
        
        # Преобразуем список в OrderedDict для сохранения порядка сортировки и возвращаем до N индекса
        return OrderedDict(movies[:n])

class Links:
    def __init__(self, path, cache_file='imdb_data.json', limit=100):
        self.movie_links = {}  # movieId → imdbId
        self.movie_titles = {} # movieId → title
        self.cache_path = cache_file
        self.limit = limit

        dir = path.rfind('/')
        
        if dir == -1:
            movies_path = 'movies.csv'  # Same directory if no '/'
        else:
            movies_path = path[:dir] + '/movies.csv'

        try:
            with open(movies_path, 'r', encoding='utf-8') as f:
                next(f)
            
                for line in f:
                    # Делим строку. Ограничение на 2 запятых
                    parts = line.strip().split(',', maxsplit=2)

                    if len(parts) >= 2:
                        # Извлекаем movieId и title
                        movieId, title = parts[0], parts[1]
                        self.movie_titles[movieId] = title

        except FileNotFoundError:
            raise FileNotFoundError(f"File {movies_path} not found.")
        
        except IOError as e:
            raise IOError(f"Error reading {movies_path}: {e}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                next(f)
            
                for i, line in enumerate(f):
            
                    if i >= self.limit:
                        break
            
                    parts = line.strip().split(',')
            
                    if len(parts) >= 2:
                        movieId, imdbId = parts[0], parts[1]
                        self.movie_links[movieId] = imdbId

        except FileNotFoundError:
            raise FileNotFoundError(f"File {movies_path} not found.")
        
        except IOError as e:
            raise IOError(f"Error reading {movies_path}: {e}")

        try:
            # Загружаем или создаём json-кэш
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.imdb_data = json.load(f)
            else:
                self.imdb_data = {}

        except json.JSONDecodeError:
            self.imdb_data = {}
        
        except IOError as e:
            raise IOError(f"Error reading {self.cache_path}: {e}")

    def _fetch_page(self, imdb_id):
        url = f'https://www.imdb.com/title/tt{imdb_id}/'
        
        # Задаем заголовки HTTP-запроса. Имитирует браузер
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            }
        
        try:
            # Отправляем GET-запрос на URL c заголоками
            response = requests.get(url, headers=headers)
            # Статус должен вернуть 200 для работы. Остальные дает исключение
            response.raise_for_status()

            time.sleep(1)
        
        except requests.Timeout:
            raise Exception(f"Request to {url} timed out.")

        except requests.RequestException:
            raise Exception("URL does not exist or given unproperly.")
        
        # Парсим через HTML с помощью BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup

    def _extract_fields(self, imdb_id, fields):
        soup = self._fetch_page(imdb_id)
        data = []


        for field in fields:
            lower = field.lower()
        
            if lower == "director":
                # Ищем ссылку на режиссера
                # Тег <a> с href - с содержимым "/name/nm" 
                tag = soup.find('a', href=re.compile(r'/name/nm'))
                
                # Если текст есть извлекаем его. Иначе "N/A"
                data.append(tag.text.strip() if tag else 'N/A')

            elif lower == "budget":

                # Ищем текст с "Budget"
                tag = soup.find(string=re.compile("Budget"))

                # Если есть берем елемент после него. Иначе путоту даем
                value = tag.find_next() if tag else None

                # Сохраняем значение если оно есть
                data.append(value.text.strip() if value else 'N/A')

            elif lower == "cumulative worldwide gross":
                # Ищем текст с "cumulative worldwide gross"
                tag = soup.find(string=re.compile("Gross worldwide"))
                
                # Если есть берем елемент после него. Иначе путоту даем
                value = tag.find_next() if tag else None

                # Сохраняем значение если оно есть
                data.append(value.text.strip() if value else 'N/A')

            elif lower == "runtime":
                # Ищем элемент с атрибутом -> data-testid="title-techspec_runtime"
                tag = soup.find('li', attrs={'data-testid': 'title-techspec_runtime'})

                # Сохраняем значение если оно есть
                data.append(tag.text.strip() if tag else 'N/A')

            else:
                data.append('N/A')

        return data

    # Функция для сохранения кэша IMDb данных в JSON
    def _save_cache(self):
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                # Сохраняем словарь imdb_data в JSON с отступами по 2
                json.dump(self.imdb_data, f, indent=2)

        except IOError as e:
            raise IOError(f"Error writing to {self.cache_path}: {e}")

    # Функция для сбора всех данных IMDb для фильмов
    def collect_all_imdb_data(self, fields):
        # Начало сбора данных
        print(f"[INFO] Collecting data for up to {self.limit} movies...")

        # Перебираем movieId / imdbId из словаря movie_links
        for i, (movieId, imdbId) in enumerate(self.movie_links.items()):
            if imdbId in self.imdb_data:
                continue
        
            try:
                # Извлекаем данные указанных полей
                values = self._extract_fields(imdbId, fields)
                # Сохраняем данные в словарь -> {imdbId: {поле: значение}}
                self.imdb_data[imdbId] = dict(zip(fields, values))
                # Сохраняем кэш
                self._save_cache()
                # Cообщение об успешном сборе
                print(f"[{i+1}/{self.limit}] Collected for tt{imdbId}")
        
            except Exception as e:
                print(f"[ERROR] Failed for tt{imdbId}: {e}")

    # Функция для парсинга бюджета + сбора
    def _parse_money(self, text):
        try:
            # Удаляем все нечисловые символы - преобразуем в целое число
            return int(re.sub(r'[^\d]', '', text))
        except:
            return 0

    # Функция для парсинга длительности фильма
    def _parse_runtime(self, text):
        # Ищем первое число в тексте. Это минуты
        match = re.search(r'(\d+)', text)
        # Если найдет. Возвращаем целое число
        return int(match.group(1)) if match else 0

    # Функция для получения IMDb данных - списка фильмов
    def get_imdb(self, list_of_movies, list_of_fields):
        result = []

        for movie_id in list_of_movies:
            # Получаем imdbId для movieId
            imdb_id = self.movie_links.get(str(movie_id))
        
            # Проверка. Есть ли данные в imdb_id + в кеше
            if imdb_id and imdb_id in self.imdb_data:
                # Извлекаем данные - imdbId
                fields = self.imdb_data[imdb_id]
                # Получаем название фильма. Если его нет используем заглушку
                title = self.movie_titles.get(str(movie_id), f"Movie {movie_id}")
                # Формирование строки - [название, значение_поля1, значение_поля2, т.д.]
                row = [title] + [fields.get(field, 'N/A') for field in list_of_fields]
                result.append(row)
        
        # Сортируем результат по названию
        return sorted(result, key=lambda x: x[0])
    
    # Tоп-N режиссеров по количеству фильмов
    def top_directors(self, n):
        counter = Counter()
        
        for data in self.imdb_data.values():
            # Если есть. Извлекаем имя Режисера. Без него будет N/A
            director = data.get('Director', 'N/A')
        
            if director != 'N/A':
                counter[director] += 1
        
        return dict(counter.most_common(n))
    
    # Tоп-N самых дорогих фильмов
    def most_expensive(self, n):
        result = []
        
        for movieId, imdbId in self.movie_links.items():
            # Получаем данные - imdbId. Если их не будет возвращает пустой dict
            data = self.imdb_data.get(imdbId, {})

            # Парсим бюджет
            budget = self._parse_money(data.get("Budget", '0'))

            # Если бюджет больше 0 - работаем дальше
            if budget > 0:
                # Получаем название фильма. Если его нет получаем заглушку
                title = self.movie_titles.get(movieId, f"Movie {movieId}")
                result.append((title, budget))
        
        # Сортируем по убыванию бюджета
        return dict(sorted(result, key=lambda x: -x[1])[:n])
    
    # Tоп-N самых прибыльных фильмов
    def most_profitable(self, n):
        result = []
        
        for movieId, imdbId in self.movie_links.items():
            # Получаем данные - imdbId
            data = self.imdb_data.get(imdbId, {})

            # Парсим бюджет + сборы
            budget = self._parse_money(data.get("Budget", '0'))
            gross = self._parse_money(data.get("Cumulative Worldwide Gross", '0'))
        
            if budget > 0 and gross > 0:
                profit = gross - budget
                title = self.movie_titles.get(movieId, f"Movie {movieId}")
                result.append((title, profit))
        
        # Сортируем по убыванию прибыли
        return dict(sorted(result, key=lambda x: -x[1])[:n])

    # Tоп-N самых длинных фильмов
    def longest(self, n):
        result = []
        
        for movieId, imdbId in self.movie_links.items():
            # Получаем данные - imdbId
            data = self.imdb_data.get(imdbId, {})
            # Парсим длительность
            runtime = self._parse_runtime(data.get("Runtime", '0'))
        
            if runtime > 0:
                # Получаем название фильма. Если его нет получаем заглушку
                title = self.movie_titles.get(movieId, f"Movie {movieId}")
                result.append((title, runtime))
        
        # Сортируем по убыванию длительности
        return dict(sorted(result, key=lambda x: -x[1])[:n])
    
    # топ-N фильмов по стоимости за минуту
    def top_cost_per_minute(self, n):
        result = []
        
        for movieId, imdbId in self.movie_links.items():
            # Получаем данные - imdbId
            data = self.imdb_data.get(imdbId, {})
            
            # Парсим бюджет
            budget = self._parse_money(data.get("Budget", '0'))

            # Парсим длительность
            runtime = self._parse_runtime(data.get("Runtime", '0'))
        
            if budget > 0 and runtime > 0:
                # Округляем до 2 знаков
                cost_per_min = round(budget / runtime, 2)
                # Получаем название фильма. Если его нет получаем заглушку
                title = self.movie_titles.get(movieId, f"Movie {movieId}")
                result.append((title, cost_per_min))
        
        # Сортируем по убыванию стоимости за минуту
        return dict(sorted(result, key=lambda x: -x[1])[:n])
    
"""
Tests
-------------------------------------------------------------------------
"""

@pytest.fixture
def rate_movies():
    return Ratings('ml-latest-small/ratings.csv').movies

@pytest.fixture
def users():
    return Ratings('ml-latest-small/ratings.csv').users

@pytest.fixture
def tags():
    return Tags('ml-latest-small/tags.csv')

@pytest.fixture
def movies():
    return Movies('ml-latest-small/movies.csv')

@pytest.fixture
def links():
    fields = ["Director", "Budget", "Cumulative Worldwide Gross", "Runtime"]
    l = Links('ml-latest-small/links.csv', limit=100)
    l.collect_all_imdb_data(fields)
    return l

class Test:
    #Ratings.Movies
    def test_dist_by_year(self, rate_movies):
        assert isinstance(rate_movies.dist_by_year(), dict)
    def test_dist_by_rating_keys(self, rate_movies):
        assert all(isinstance(k, float) for k in rate_movies.dist_by_rating().keys())
    def test_top_by_num_of_ratings(self, rate_movies):
        assert all(isinstance(v, int) for v in rate_movies.top_by_num_of_ratings(10).values())
    def test_top_by_ratings_sorted(self, rate_movies):
        values = list(rate_movies.top_by_ratings(10).values())
        assert values == sorted(values, reverse=True)
    def test_top_movie_controversial(self, rate_movies):
        assert isinstance(rate_movies.top_controversial(10), dict)
    def test_ratings_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Ratings('nonexistent/ratings.csv')

    #RatingsUsers
    def test_dist_by_num_of_ratings(self, users):
        assert isinstance(users.dist_by_num_of_ratings(), dict)
    def test_dist_by_metric(self, users):
        assert all(isinstance(k, float) for k in users.dist_by_metric().keys())
    def test_top_user_controversial(self, users):
        result = list(users.top_controversial(10).values())
        assert result == sorted(result, reverse=True)

    #Tags
    def test_most_words(self, tags):
        assert isinstance(tags.most_words(10), dict)
    def test_longest_tags(self, tags):
        assert isinstance(tags.longest(10), list)
    def test_most_words_and_longest(self, tags):
        assert isinstance(tags.most_words_and_longest(10), list)
    def test_most_popular(self, tags):
        assert isinstance(tags.most_popular(10), dict)
    def test_tags_with(self, tags):
        result = tags.tags_with('Black')
        assert set(result) == {'Black comedy', 'black and white', 'black comedy', 'black hole', 'black humor', 'black humour', 'black-and-white'}
    def test_tags_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Tags('nonexistent/tags.csv')
    def test_tags_empty_tags(self, tmp_path):
        empty_file = tmp_path / "tags.csv"
        empty_file.write_text("userId,movieId,tag,timestamp\n", encoding='utf-8')
        tags = Tags(str(empty_file))
        assert len(tags.tags) == 0
        assert len(tags.unique_tags) == 0

    #Movies
    def test_dist_by_release(self, movies):
        result = movies.dist_by_release()
        assert list(result.values()) == sorted(result.values(), reverse=True)
    def test_dist_by_genres(self, movies):
        assert all(isinstance(k, str) for k in movies.dist_by_genres().keys())
    def test_most_genres(self, movies):
        assert isinstance(movies.most_genres(10), OrderedDict)
    def test_movies_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Movies('nonexistent/movies.csv')
    def test_movies_no_genres(self, tmp_path):
        test_file = tmp_path / "movies.csv"
        test_file.write_text("movieId,title,genres\n1,Movie,(no genres listed)\n", encoding='utf-8')
        movies = Movies(str(test_file))
        assert movies.dist_by_genres() == {}

    #Links
    def test_get_imdb(self, links):
        result = links.get_imdb([1, 2, 3], ['Director', 'Budget'])
        assert all(isinstance(row, list) for row in result)
    def test_top_directors(self, links):
        assert isinstance(links.top_directors(2), dict)    
    def test_most_expensive(self, links):
        assert all(isinstance(key, str) for key in links.most_expensive(2).keys())
    def test_most_profitable(self, links):
        assert all(isinstance(value, int) for value in links.most_profitable(2).values())
    def test_longest_link(self, links):
        assert isinstance(links.longest(5), dict)
    def test_top_cost_per_minute(self, links):
        result = links.top_cost_per_minute(5)
        assert list(result.values()) == sorted(result.values(), reverse=True)
    def test_links_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Links('nonexistent/links.csv')
    def test_links_corrupted_cache(self, tmp_path):
        cache_file = tmp_path / "corrupted.json"
        cache_file.write_text("invalid json", encoding='utf-8')
        links = Links('ml-latest-small/links.csv', cache_file=str(cache_file))
        assert links.imdb_data == {}
    def test_links_invalid_movie_id(self, links):
        result = links.get_imdb([999999], ['Director'])
        assert result == []

if __name__ == '__main__':
    ratings = Ratings('ml-latest-small/ratings.csv')
    movies = ratings.movies
    # print(movies.dist_by_year())
    # print(movies.dist_by_rating())
    # print(movies.top_by_num_of_ratings(10))
    # print(movies.top_by_ratings(10))
    # print(movies.top_controversial(10))
    users = ratings.users
    # print(users.dist_by_num_of_ratings())
    # print(users.dist_by_metric())
    # print(users.top_controversial(10))

    tags = Tags('ml-latest-small/tags.csv')
    # print(tags.most_words(10))
    # print(tags.longest(10))
    # print(tags.most_words_and_longest(10))
    # print(tags.most_popular(10))
    # print(tags.tags_with('Black'))

    movies = Movies('ml-latest-small/movies.csv')
    # print(movies.dist_by_release())
    # print(movies.dist_by_genres())
    # print(movies.most_genres(10))

    links = Links('ml-latest-small/links.csv', limit=100)
    fields = ["Director", "Budget", "Cumulative Worldwide Gross", "Runtime"]
    links.collect_all_imdb_data(fields)
    # print(links.get_imdb([1, 2, 3], fields))
    # print(links.top_directors(2))
    # print(links.most_expensive(2))
    # print(links.most_profitable(2))
    # print(links.longest(2))
    # print(links.top_cost_per_minute(5))