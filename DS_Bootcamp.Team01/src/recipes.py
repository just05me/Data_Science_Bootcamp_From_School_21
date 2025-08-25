# -*- coding: utf-8 -*-
"""
Модуль для анализа рецептов и пищевой ценности
Содержит классы для работы с данными о питании и рекомендациями рецептов
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
import re


class NutritionFacts:
    """Класс для работы с данными о пищевой ценности ингредиентов"""
    
    def __init__(self, nutrition_file, daily_values_file):
        """
        Инициализация класса
        
        Args:
            nutrition_file (str): Путь к файлу с данными о питании
            daily_values_file (str): Путь к файлу с дневными нормами
        """
        self.nutrition_file = nutrition_file
        self.daily_values_file = daily_values_file
        self.nutrition_data = None
        self.daily_values = None
        self._load_data()
    
    def _load_data(self):
        """
        Загрузка данных о питании и дневных нормах
        
        Загружает CSV файлы с данными о питании ингредиентов и дневными нормами
        питательных веществ. Обрабатывает ошибки загрузки файлов.
        """
        try:
            # Загружаем данные о питании
            self.nutrition_data = pd.read_csv(self.nutrition_file)
            print(f"Данные о питании загружены: {len(self.nutrition_data)} записей")
            
            # Загружаем дневные нормы
            self.daily_values = pd.read_csv(self.daily_values_file)
            print(f"Дневные нормы загружены: {len(self.daily_values)} питательных веществ")
            
        except FileNotFoundError as e:
            print(f"Файл не найден: {e}")
            self.nutrition_data = pd.DataFrame()
            self.daily_values = pd.DataFrame()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.nutrition_data = pd.DataFrame()
            self.daily_values = pd.DataFrame()
    
    def transform_data(self):
        """
        Трансформация данных о питании в проценты от дневной нормы
        
        Преобразует абсолютные значения питательных веществ в проценты
        от рекомендуемой дневной нормы потребления.
        
        Returns:
            pd.DataFrame: Трансформированные данные с процентами от дневной нормы
        """
        if self.nutrition_data.empty or self.daily_values.empty:
            print("Нет данных для трансформации")
            return pd.DataFrame()
        
        try:
            # Очищаем названия питательных веществ от лишних пробелов
            self.daily_values['nutrient'] = self.daily_values['nutrient'].str.strip()
            
            # Создаем копию данных для работы
            transformed = self.nutrition_data.copy()
            
            # Преобразуем каждое питательное вещество в проценты от дневной нормы
            for _, nutrient_row in self.daily_values.iterrows():
                nutrient_name = nutrient_row['nutrient']
                daily_value = nutrient_row['daily_value']
                
                # Проверяем, есть ли колонка с этим питательным веществом
                if nutrient_name in transformed.columns:
                    # Заменяем NaN на 0 для корректных вычислений
                    transformed[nutrient_name] = transformed[nutrient_name].fillna(0)
                    
                    # Вычисляем процент от дневной нормы
                    transformed[nutrient_name] = (transformed[nutrient_name] / daily_value) * 100
            
            print("Данные о питании успешно трансформированы")
            return transformed
            
        except Exception as e:
            print(f"Ошибка трансформации данных: {e}")
            return pd.DataFrame()
    
    def get_ingredient_nutrition(self, ingredient_name):
        """
        Получение данных о питании для конкретного ингредиента
        
        Args:
            ingredient_name (str): Название ингредиента
            
        Returns:
            dict: Данные о питании ингредиента
        """
        if self.nutrition_data.empty:
            return {}
        
        try:
            # Ищем колонку с названием ингредиента (нечувствительно к регистру)
            ingredient_col = None
            for col in self.nutrition_data.columns:
                if col.lower() == 'ingredient':
                    ingredient_col = col
                    break
            
            if ingredient_col is None:
                print("Колонка с названиями ингредиентов не найдена")
                return {}
            
            # Ищем ингредиент без учета регистра
            ingredient_data = self.nutrition_data[
                self.nutrition_data[ingredient_col].str.lower() == ingredient_name.lower()
            ]
            
            if ingredient_data.empty:
                print(f"Ингредиент '{ingredient_name}' не найден в базе данных")
                return {}
            
            # Возвращаем данные первого найденного ингредиента
            return ingredient_data.iloc[0].to_dict()
            
        except Exception as e:
            print(f"Ошибка поиска ингредиента '{ingredient_name}': {e}")
            return {}


class RecipeRecommender:
    """Класс для рекомендации похожих рецептов"""
    
    def __init__(self, recipes_file):
        """
        Инициализация класса
        
        Args:
            recipes_file (str): Путь к файлу с рецептами
        """
        self.recipes_file = recipes_file
        self.recipes_data = None
        self.vectorizer = None
        self.ingredient_matrix = None
        self._load_data()
        self._prepare_similarity_matrix()
    
    def _load_data(self):
        """
        Загрузка данных о рецептах
        
        Загружает CSV файл с рецептами и обрабатывает возможные ошибки
        при загрузке файла.
        """
        try:
            self.recipes_data = pd.read_csv(self.recipes_file)
            print(f"Рецепты загружены: {len(self.recipes_data)} записей")
            
            # Проверяем наличие необходимых колонок
            required_columns = ['rating']
            missing_columns = [col for col in required_columns if col not in self.recipes_data.columns]
            
            if missing_columns:
                print(f"Предупреждение: отсутствуют колонки: {missing_columns}")
                
        except FileNotFoundError as e:
            print(f"Файл с рецептами не найден: {e}")
            self.recipes_data = pd.DataFrame()
        except Exception as e:
            print(f"Ошибка загрузки рецептов: {e}")
            self.recipes_data = pd.DataFrame()
    
    def _prepare_similarity_matrix(self):
        """
        Подготовка матрицы сходства для поиска похожих рецептов
        
        Создает векторное представление ингредиентов для каждого рецепта
        и подготавливает матрицу для быстрого поиска похожих рецептов.
        """
        if self.recipes_data.empty:
            print("Нет данных о рецептах для подготовки матрицы сходства")
            return
        
        try:
            # Создаем список ингредиентов для каждого рецепта
            if 'ingredients_list' not in self.recipes_data.columns:
                # Если колонки нет, создаем её из бинарных колонок ингредиентов
                ingredient_cols = [col for col in self.recipes_data.columns 
                                 if col not in ['rating', 'title', 'calories', 'protein', 'fat', 'sodium']]
                
                print(f"Создаем список ингредиентов из {len(ingredient_cols)} колонок")
                
                self.recipes_data['ingredients_list'] = self.recipes_data[ingredient_cols].apply(
                    lambda row: ', '.join([col for col in ingredient_cols if row[col] == 1]), 
                    axis=1
                )
            
            # Векторизация ингредиентов с помощью CountVectorizer
            self.vectorizer = CountVectorizer(
                tokenizer=lambda x: [item.strip() for item in x.split(',') if item.strip()],
                lowercase=True,
                min_df=1  # Минимальная частота документа
            )
            
            # Создание матрицы признаков для всех рецептов
            ingredient_lists = self.recipes_data['ingredients_list'].fillna('')
            self.ingredient_matrix = self.vectorizer.fit_transform(ingredient_lists)
            
            print(f"Матрица сходства подготовлена: {self.ingredient_matrix.shape}")
            
        except Exception as e:
            print(f"Ошибка подготовки матрицы сходства: {e}")
            self.vectorizer = None
            self.ingredient_matrix = None
    
    def find_similar_recipes(self, input_ingredients, top_n=3):
        """
        Поиск похожих рецептов по ингредиентам
        
        Использует косинусное сходство для поиска рецептов, наиболее
        похожих по составу ингредиентов.
        
        Args:
            input_ingredients (str): Список ингредиентов через запятую
            top_n (int): Количество возвращаемых рецептов
            
        Returns:
            pd.DataFrame: Похожие рецепты с оценкой сходства
        """
        if self.ingredient_matrix is None or self.vectorizer is None:
            print("Матрица сходства не подготовлена")
            return pd.DataFrame()
        
        try:
            # Векторизация входных ингредиентов
            input_vec = self.vectorizer.transform([input_ingredients])
            
            # Вычисление косинусного сходства между входными ингредиентами и всеми рецептами
            similarities = cosine_similarity(input_vec, self.ingredient_matrix).flatten()
            
            # Получение топ-N индексов по убыванию сходства
            top_indices = similarities.argsort()[-top_n:][::-1]
            
            # Фильтрация по сходству (убираем рецепты с нулевым сходством)
            top_indices = [idx for idx in top_indices if similarities[idx] > 0]
            
            if not top_indices:
                print("Не найдено похожих рецептов")
                return pd.DataFrame()
            
            # Получение результатов
            results = self.recipes_data.iloc[top_indices].copy()
            
            # Добавление информации о сходстве
            results['similarity_score'] = similarities[top_indices]
            
            # Сортировка по сходству (от большего к меньшему)
            results = results.sort_values('similarity_score', ascending=False)
            
            # Выбор нужных колонок для отображения
            columns_to_show = ['title', 'rating', 'url'] if 'url' in results.columns else ['rating']
            available_columns = [col for col in columns_to_show if col in results.columns]
            
            # Возвращаем результаты с колонкой сходства
            return results[available_columns + ['similarity_score']]
            
        except Exception as e:
            print(f"Ошибка поиска похожих рецептов: {e}")
            return pd.DataFrame()
    
    def get_recipe_by_ingredients(self, ingredients_list):
        """
        Получение рецептов, содержащих указанные ингредиенты
        
        Ищет рецепты, которые содержат все указанные ингредиенты.
        
        Args:
            ingredients_list (list): Список ингредиентов для поиска
            
        Returns:
            pd.DataFrame: Подходящие рецепты
        """
        if self.recipes_data.empty:
            return pd.DataFrame()
        
        try:
            # Поиск рецептов, содержащих все указанные ингредиенты
            matching_recipes = []
            
            for _, recipe in self.recipes_data.iterrows():
                recipe_ingredients = recipe.get('ingredients_list', '')
                
                if isinstance(recipe_ingredients, str):
                    # Разбиваем список ингредиентов рецепта на отдельные элементы
                    recipe_ingredients = [ing.strip().lower() for ing in recipe_ingredients.split(',')]
                    
                    # Проверяем, содержит ли рецепт все указанные ингредиенты
                    if all(ing.lower() in recipe_ingredients for ing in ingredients_list):
                        matching_recipes.append(recipe)
            
            if matching_recipes:
                print(f"Найдено {len(matching_recipes)} рецептов с указанными ингредиентами")
                return pd.DataFrame(matching_recipes)
            else:
                print("Не найдено рецептов с указанными ингредиентами")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Ошибка поиска рецептов по ингредиентам: {e}")
            return pd.DataFrame()


# Вспомогательные функции для работы с моделями

def load_model(model_path):
    """
    Загрузка обученной модели из файла
    
    Args:
        model_path (str): Путь к файлу модели
        
    Returns:
        object: Загруженная модель или None в случае ошибки
    """
    try:
        import pickle
        with open(model_path, "rb") as file:
            model = pickle.load(file)
        print(f"Модель успешно загружена из {model_path}")
        return model
    except FileNotFoundError:
        print(f"Файл модели не найден: {model_path}")
        return None
    except Exception as e:
        print(f"Ошибка загрузки модели: {e}")
        return None


def forecast_rating(model, ingredients):
    """
    Прогнозирование рейтинга блюда на основе ингредиентов
    
    Использует обученную модель для предсказания рейтинга блюда
    по списку ингредиентов.
    
    Args:
        model: Обученная модель машинного обучения
        ingredients (list): Список ингредиентов
        
    Returns:
        str: Прогнозируемый класс рейтинга (bad, so-so, great)
    """
    if model is None:
        print("Модель не загружена, возвращаю значение по умолчанию")
        return "so-so"  # Значение по умолчанию
    
    try:
        # Преобразование ингредиентов в строку
        ingredients_str = ", ".join(ingredients)
        
        # Прогнозирование с помощью модели
        prediction = model.predict([ingredients_str])[0]
        
        # Преобразование числового прогноза в категории, если нужно
        if isinstance(prediction, (int, float)):
            if prediction <= 1:
                return "bad"
            elif prediction <= 3:
                return "so-so"
            else:
                return "great"
        
        return prediction
        
    except Exception as e:
        print(f"Ошибка прогнозирования: {e}")
        return "so-so"


class DailyMenuGenerator:
    """Класс для генерации дневного меню"""
    
    def __init__(self, recipes_file, nutrition_file, daily_values_file):
        """
        Инициализация класса
        
        Args:
            recipes_file (str): Путь к файлу с рецептами
            nutrition_file (str): Путь к файлу с данными о питании
            daily_values_file (str): Путь к файлу с дневными нормами
        """
        self.recipes_file = recipes_file
        self.nutrition_file = nutrition_file
        self.daily_values_file = daily_values_file
        self.recipes_data = None
        self.nutrition_data = None
        self.daily_values = None
        self._load_data()
    
    def _load_data(self):
        """
        Загрузка данных о рецептах, питании и дневных нормах
        """
        try:
            # Загружаем рецепты
            self.recipes_data = pd.read_csv(self.recipes_file)
            print(f"Рецепты для меню загружены: {len(self.recipes_data)} записей")
            
            # Загружаем данные о питании
            self.nutrition_data = pd.read_csv(self.nutrition_file)
            print(f"Данные о питании для меню загружены: {len(self.nutrition_data)} записей")
            
            # Загружаем дневные нормы
            self.daily_values = pd.read_csv(self.daily_values_file)
            print(f"Дневные нормы для меню загружены: {len(self.daily_values)} питательных веществ")
            
        except FileNotFoundError as e:
            print(f"Файл не найден: {e}")
            self.recipes_data = pd.DataFrame()
            self.nutrition_data = pd.DataFrame()
            self.daily_values = pd.DataFrame()
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.recipes_data = pd.DataFrame()
            self.nutrition_data = pd.DataFrame()
            self.daily_values = pd.DataFrame()
    
    def _categorize_meal_time(self, recipe_title, recipe_ingredients):
        """
        Категоризация рецепта по времени приема пищи
        
        Args:
            recipe_title (str): Название рецепта
            recipe_ingredients (str): Список ингредиентов
            
        Returns:
            str: Категория времени приема пищи (breakfast, lunch, dinner)
        """
        title_lower = recipe_title.lower()
        ingredients_lower = recipe_ingredients.lower()
        
        # Ключевые слова для завтрака
        breakfast_keywords = [
            'breakfast', 'brunch', 'pancake', 'waffle', 'omelet', 'omelette', 
            'muffin', 'cereal', 'oatmeal', 'granola', 'yogurt', 'smoothie',
            'toast', 'bagel', 'croissant', 'french toast', 'eggs benedict'
        ]
        
        # Ключевые слова для обеда
        lunch_keywords = [
            'lunch', 'sandwich', 'salad', 'soup', 'pasta', 'pizza', 'burger',
            'wrap', 'quesadilla', 'taco', 'burrito', 'stir-fry', 'curry'
        ]
        
        # Ключевые слова для ужина
        dinner_keywords = [
            'dinner', 'supper', 'roast', 'grill', 'bake', 'stew', 'casserole',
            'lasagna', 'meatloaf', 'steak', 'chicken', 'fish', 'seafood'
        ]
        
        # Проверяем название рецепта
        for keyword in breakfast_keywords:
            if keyword in title_lower:
                return 'breakfast'
        
        for keyword in lunch_keywords:
            if keyword in title_lower:
                return 'lunch'
        
        for keyword in dinner_keywords:
            if keyword in title_lower:
                return 'dinner'
        
        # Если название не помогло, проверяем ингредиенты
        for keyword in breakfast_keywords:
            if keyword in ingredients_lower:
                return 'breakfast'
        
        for keyword in lunch_keywords:
            if keyword in ingredients_lower:
                return 'lunch'
        
        for keyword in dinner_keywords:
            if keyword in ingredients_lower:
                return 'dinner'
        
        # По умолчанию считаем ужином
        return 'dinner'
    
    def _calculate_recipe_nutrition(self, recipe_ingredients):
        """
        Расчет пищевой ценности рецепта на основе ингредиентов
        
        Args:
            recipe_ingredients (str): Список ингредиентов рецепта
            
        Returns:
            dict: Словарь с пищевой ценностью рецепта
        """
        if self.nutrition_data.empty or self.daily_values.empty:
            return {}
        
        try:
            # Разбиваем ингредиенты на отдельные элементы
            ingredients_list = [ing.strip().lower() for ing in recipe_ingredients.split(',') if ing.strip()]
            
            # Ищем колонку с названием ингредиента
            ingredient_col = None
            for col in self.nutrition_data.columns:
                if col.lower() == 'ingredient':
                    ingredient_col = col
                    break
            
            if ingredient_col is None:
                return {}
            
            # Собираем данные о питании для всех ингредиентов
            recipe_nutrition = {}
            
            for ingredient in ingredients_list:
                # Ищем ингредиент в базе данных
                ingredient_data = self.nutrition_data[
                    self.nutrition_data[ingredient_col].str.lower() == ingredient
                ]
                
                if not ingredient_data.empty:
                    # Добавляем данные о питании для каждого питательного вещества
                    for col in ingredient_data.columns:
                        if col != ingredient_col and col in self.daily_values['nutrient'].values:
                            value = ingredient_data[col].iloc[0]
                            if pd.notna(value) and value > 0:
                                if col not in recipe_nutrition:
                                    recipe_nutrition[col] = 0
                                recipe_nutrition[col] += value
            
            return recipe_nutrition
            
        except Exception as e:
            print(f"Ошибка расчета пищевой ценности рецепта: {e}")
            return {}
    
    def _calculate_nutrition_score(self, recipe_nutrition):
        """
        Расчет оценки пищевой ценности рецепта
        
        Args:
            recipe_nutrition (dict): Словарь с пищевой ценностью рецепта
            
        Returns:
            float: Оценка пищевой ценности (0-100)
        """
        if not recipe_nutrition:
            return 0.0
        
        try:
            total_score = 0
            nutrient_count = 0
            
            for nutrient, value in recipe_nutrition.items():
                # Ищем дневную норму для этого питательного вещества
                daily_value = self.daily_values[
                    self.daily_values['nutrient'] == nutrient
                ]['daily_value'].values
                
                if len(daily_value) > 0:
                    daily_value = daily_value[0]
                    
                    # Вычисляем процент от дневной нормы
                    percentage = (value / daily_value) * 100
                    
                    # Оценка: оптимально 20-30% от дневной нормы за прием пищи
                    if 20 <= percentage <= 30:
                        score = 100  # Отлично
                    elif 15 <= percentage <= 40:
                        score = 80   # Хорошо
                    elif 10 <= percentage <= 50:
                        score = 60   # Удовлетворительно
                    elif 5 <= percentage <= 70:
                        score = 40   # Плохо
                    else:
                        score = 20   # Очень плохо
                    
                    total_score += score
                    nutrient_count += 1
            
            if nutrient_count == 0:
                return 0.0
            
            return total_score / nutrient_count
            
        except Exception as e:
            print(f"Ошибка расчета оценки пищевой ценности: {e}")
            return 0.0
    
    def generate_daily_menu(self):
        """
        Генерация дневного меню
        
        Returns:
            dict: Словарь с меню для завтрака, обеда и ужина
        """
        if self.recipes_data.empty:
            print("Нет данных о рецептах для генерации меню")
            return {}
        
        try:
            # Создаем список ингредиентов для каждого рецепта, если его нет
            if 'ingredients_list' not in self.recipes_data.columns:
                ingredient_cols = [col for col in self.recipes_data.columns 
                                 if col not in ['rating', 'title', 'calories', 'protein', 'fat', 'sodium']]
                
                self.recipes_data['ingredients_list'] = self.recipes_data[ingredient_cols].apply(
                    lambda row: ', '.join([col for col in ingredient_cols if row[col] == 1]), 
                    axis=1
                )
            
            # Категоризируем рецепты по времени приема пищи
            self.recipes_data['meal_time'] = self.recipes_data.apply(
                lambda row: self._categorize_meal_time(
                    row.get('title', ''), 
                    row.get('ingredients_list', '')
                ), 
                axis=1
            )
            
            # Вычисляем пищевую ценность для каждого рецепта
            self.recipes_data['nutrition_score'] = self.recipes_data['ingredients_list'].apply(
                self._calculate_recipe_nutrition
            )
            
            # Вычисляем общую оценку рецепта (рейтинг + пищевая ценность)
            self.recipes_data['total_score'] = self.recipes_data.apply(
                lambda row: (
                    (row.get('rating', 0) * 0.6) + 
                    (self._calculate_nutrition_score(row.get('nutrition_score', {})) * 0.4)
                ), 
                axis=1
            )
            
            # Генерируем меню для каждого времени приема пищи
            daily_menu = {}
            
            for meal_time in ['breakfast', 'lunch', 'dinner']:
                # Фильтруем рецепты для конкретного времени приема пищи
                meal_recipes = self.recipes_data[
                    self.recipes_data['meal_time'] == meal_time
                ].copy()
                
                if not meal_recipes.empty:
                    # Сортируем по общей оценке и выбираем лучший
                    best_recipe = meal_recipes.sort_values('total_score', ascending=False).iloc[0]
                    
                    daily_menu[meal_time] = {
                        'title': best_recipe.get('title', 'Без названия'),
                        'rating': best_recipe.get('rating', 0),
                        'ingredients': best_recipe.get('ingredients_list', ''),
                        'nutrition': best_recipe.get('nutrition_score', {}),
                        'url': best_recipe.get('url', ''),
                        'total_score': best_recipe.get('total_score', 0)
                    }
                else:
                    # Если нет рецептов для конкретного времени, берем случайный
                    random_recipe = self.recipes_data.sample(n=1).iloc[0]
                    daily_menu[meal_time] = {
                        'title': random_recipe.get('title', 'Без названия'),
                        'rating': random_recipe.get('rating', 0),
                        'ingredients': random_recipe.get('ingredients_list', ''),
                        'nutrition': random_recipe.get('nutrition_score', {}),
                        'url': random_recipe.get('url', ''),
                        'total_score': random_recipe.get('total_score', 0)
                    }
            
            print("Дневное меню успешно сгенерировано")
            return daily_menu
            
        except Exception as e:
            print(f"Ошибка генерации дневного меню: {e}")
            return {}
    
    def display_daily_menu(self, daily_menu):
        """
        Отображение дневного меню в красивом формате
        
        Args:
            daily_menu (dict): Словарь с дневным меню
        """
        if not daily_menu:
            print("Нет данных для отображения меню")
            return
        
        try:
            # Отображение завтрака
            if 'breakfast' in daily_menu:
                breakfast = daily_menu['breakfast']
                print("ЗАВТРАК")
                print("-" * 21)
                print(f"{breakfast['title']} (рейтинг: {breakfast['rating']:.3f})")
                print("Ингредиенты:")
                
                ingredients = breakfast['ingredients'].split(',')
                for ingredient in ingredients:
                    if ingredient.strip():
                        print(f"- {ingredient.strip()}")
                
                print("Питательные вещества:")
                for nutrient, value in breakfast['nutrition'].items():
                    if pd.notna(value) and value > 0:
                        # Ищем дневную норму
                        daily_value = self.daily_values[
                            self.daily_values['nutrient'] == nutrient
                        ]['daily_value'].values
                        
                        if len(daily_value) > 0:
                            percentage = (value / daily_value[0]) * 100
                            print(f"- {nutrient}: {percentage:.1f}%")
                
                if breakfast['url']:
                    print(f"URL: {breakfast['url']}")
                print()
            
            # Отображение обеда
            if 'lunch' in daily_menu:
                lunch = daily_menu['lunch']
                print("ОБЕД")
                print("-" * 6)
                print(f"{lunch['title']} (рейтинг: {lunch['rating']:.3f})")
                print("Ингредиенты:")
                
                ingredients = lunch['ingredients'].split(',')
                for ingredient in ingredients:
                    if ingredient.strip():
                        print(f"- {ingredient.strip()}")
                
                print("Питательные вещества:")
                for nutrient, value in lunch['nutrition'].items():
                    if pd.notna(value) and value > 0:
                        daily_value = self.daily_values[
                            self.daily_values['nutrient'] == nutrient
                        ]['daily_value'].values
                        
                        if len(daily_value) > 0:
                            percentage = (value / daily_value[0]) * 100
                            print(f"- {nutrient}: {percentage:.1f}%")
                
                if lunch['url']:
                    print(f"URL: {lunch['url']}")
                print()
            
            # Отображение ужина
            if 'dinner' in daily_menu:
                dinner = daily_menu['dinner']
                print("УЖИН")
                print("-" * 6)
                print(f"{dinner['title']} (рейтинг: {dinner['rating']:.3f})")
                print("Ингредиенты:")
                
                ingredients = dinner['ingredients'].split(',')
                for ingredient in ingredients:
                    if ingredient.strip():
                        print(f"- {ingredient.strip()}")
                
                print("Питательные вещества:")
                for nutrient, value in dinner['nutrition'].items():
                    if pd.notna(value) and value > 0:
                        daily_value = self.daily_values[
                            self.daily_values['nutrient'] == nutrient
                        ]['daily_value'].values
                        
                        if len(daily_value) > 0:
                            percentage = (value / daily_value[0]) * 100
                            print(f"- {nutrient}: {percentage:.1f}%")
                
                if dinner['url']:
                    print(f"URL: {dinner['url']}")
                print()
                
        except Exception as e:
            print(f"Ошибка отображения меню: {e}")


if __name__ == "__main__":
    """
    Тестирование модуля при запуске напрямую
    
    Проверяет корректность создания классов и загрузки данных
    """
    print("Тестирование модуля recipes.py")
    print("=" * 50)
    
    # Тест класса NutritionFacts
    print("\n1. Тестирование NutritionFacts...")
    try:
        nutrition = NutritionFacts("nutrition_facts.csv", "daily_values.csv")
        print("✓ NutritionFacts создан успешно")
        
        # Тест трансформации данных
        if not nutrition.nutrition_data.empty:
            transformed = nutrition.transform_data()
            if not transformed.empty:
                print("✓ Трансформация данных работает")
            else:
                print("✗ Трансформация данных не работает")
        
    except Exception as e:
        print(f"✗ Ошибка создания NutritionFacts: {e}")
    
    # Тест класса RecipeRecommender
    print("\n2. Тестирование RecipeRecommender...")
    try:
        recommender = RecipeRecommender("recipes.csv")
        print("✓ RecipeRecommender создан успешно")
        
        # Тест поиска похожих рецептов
        if not recommender.recipes_data.empty:
            test_ingredients = "milk, honey"
            similar = recommender.find_similar_recipes(test_ingredients, top_n=2)
            if not similar.empty:
                print("✓ Поиск похожих рецептов работает")
            else:
                print("✗ Поиск похожих рецептов не работает")
        
    except Exception as e:
        print(f"✗ Ошибка создания RecipeRecommender: {e}")
    
    # Тест класса DailyMenuGenerator
    print("\n3. Тестирование DailyMenuGenerator...")
    try:
        menu_generator = DailyMenuGenerator("recipes.csv", "nutrition_facts.csv", "daily_values.csv")
        print("✓ DailyMenuGenerator создан успешно")
        
        # Тест генерации меню
        if not menu_generator.recipes_data.empty:
            daily_menu = menu_generator.generate_daily_menu()
            if daily_menu:
                print("✓ Генерация меню работает")
                print("\nПример сгенерированного меню:")
                menu_generator.display_daily_menu(daily_menu)
            else:
                print("✗ Генерация меню не работает")
        
    except Exception as e:
        print(f"✗ Ошибка создания DailyMenuGenerator: {e}")
    
    print("\n" + "=" * 50)
    print("Тестирование завершено")