import argparse
import pickle
import pandas as pd
from recipes import NutritionFacts, RecipeRecommender, DailyMenuGenerator

def load_model(model_path):
    """
    Загружает обученную модель из файла
    
    Args:
        model_path (str): Путь к файлу модели
        
    Returns:
        object: Загруженная модель или None в случае ошибки
    """
    try:
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
    Прогнозирует рейтинг блюда на основе ингредиентов
    
    Args:
        model: Обученная модель машинного обучения (может быть None)
        ingredients (list): Список ингредиентов
        
    Returns:
        str: Прогнозируемый класс рейтинга (bad, so-so, great)
        
    Raises:
        SystemExit: Если происходит ошибка во время прогнозирования
    """
    try:
        # Если модель не загружена, используем простую логику
        if model is None:
            print("Модель не загружена, использую простую логику оценки")
            
            # Простая логика оценки на основе ключевых слов
            ingredients_str = ", ".join(ingredients).lower()
            
            # Определяем рейтинг по ключевым словам
            bad_keywords = ['rotten', 'spoiled', 'artificial', 'processed', 'old', 'stale']
            great_keywords = ['fresh', 'organic', 'natural', 'chocolate', 'honey', 'fruits']
            
            bad_count = sum(1 for word in bad_keywords if word in ingredients_str)
            great_count = sum(1 for word in great_keywords if word in ingredients_str)
            
            if bad_count > great_count:
                return "bad"
            elif great_count > bad_count:
                return "great"
            else:
                return "so-so"
        
        # Если модель загружена, используем её для прогнозирования
        ingredients_str = ", ".join(ingredients)
        
        # В реальном случае здесь должна быть предобработка данных
        # как при обучении модели. Для простоты предполагаем, что модель
        # использует CountVectorizer на тексте ингредиентов
        prediction = model.predict([ingredients_str])[0]
        
        # Преобразуем числовой прогноз в категории, если нужно
        if isinstance(prediction, (int, float)):
            if prediction <= 1:
                return "bad"
            elif prediction <= 3:
                return "so-so"
            else:
                return "great"
        
        return prediction
        
    except Exception as e:
        print(f"Ошибка во время прогнозирования: {e}")
        # В случае ошибки возвращаем средний рейтинг
        return "so-so"

def main():
    """
    Основная функция программы
    
    Обрабатывает аргументы командной строки, загружает модель и данные,
    выполняет прогнозирование рейтинга, показывает пищевую ценность
    и находит похожие рецепты
    """
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="Предиктор здоровой и вкусной еды.")
    parser.add_argument("ingredients", type=str, nargs='?', help="Список ингредиентов через запятую")
    parser.add_argument("--menu", action="store_true", help="Сгенерировать дневное меню")
    args = parser.parse_args()

    # Если запрошено меню, генерируем его
    if args.menu:
        print("Генерация дневного меню...")
        menu_generator = DailyMenuGenerator("recipes.csv", "nutrition_facts.csv", "daily_values.csv")
        daily_menu = menu_generator.generate_daily_menu()
        
        if daily_menu:
            print("\n" + "=" * 50)
            print("ДНЕВНОЕ МЕНЮ")
            print("=" * 50)
            menu_generator.display_daily_menu(daily_menu)
        else:
            print("Не удалось сгенерировать дневное меню")
        return

    # Проверяем, что ингредиенты указаны
    if not args.ingredients:
        print("Ошибка: необходимо указать ингредиенты или использовать опцию --menu")
        parser.print_help()
        return

    # Подготавливаем список ингредиентов, убирая лишние пробелы
    ingredients_list = [ingredient.strip() for ingredient in args.ingredients.split(",")]

    # Загружаем необходимые модули и данные
    print("Загрузка данных...")
    nutrition = NutritionFacts("nutrition_facts.csv", "daily_values.csv")
    recommender = RecipeRecommender("recipes.csv")
    model = load_model("best_model.pkl")

    # Прогнозируем рейтинг блюда
    print("\nI. НАШ ПРОГНОЗ")
    predicted_class = forecast_rating(model, ingredients_list)
    
    # Выводим результат прогноза на русском языке
    if predicted_class == "bad":
        print("Возможно, вам понравится, но по нашему мнению, это плохая идея - готовить блюдо с таким набором ингредиентов.")
    elif predicted_class == "so-so":
        print("Может быть нормально, но возможно, это не лучшая комбинация.")
    else:
        print("Похоже на отличное блюдо! Хороший выбор!")

    # Трансформируем данные о питании один раз
    print("\nЗагрузка данных о питании...")
    try:
        transformed_data = nutrition.transform_data()
    except Exception as e:
        print(f"Ошибка трансформации данных о питании: {e}")
        exit(1)

    # Отображаем информацию о пищевой ценности
    print("\nII. ПИЩЕВАЯ ЦЕННОСТЬ")
    for ingredient in ingredients_list:
        print(f"\n{ingredient.capitalize()}:")
        
        # Ищем колонку с названием ингредиента (нечувствительно к регистру)
        ingredient_col = None
        for col in transformed_data.columns:
            if col.lower() == 'ingredient':
                ingredient_col = col
                break
        
        if ingredient_col is None:
            print("  Колонка с названиями ингредиентов не найдена в данных")
            continue
        
        # Ищем данные о питании для ингредиента
        facts = transformed_data[transformed_data[ingredient_col].str.lower() == ingredient.lower()]
        
        if facts.empty:
            print("  Данные о питании недоступны.")
        else:
            # Убираем колонку с названием ингредиента и показываем остальные данные
            nutrition_info = facts.drop(columns=[ingredient_col])
            print(nutrition_info.to_string(index=False))

    # Находим и отображаем похожие рецепты
    print("\nIII. ТОП-3 ПОХОЖИХ РЕЦЕПТА:")
    try:
        # Ищем похожие рецепты на основе ингредиентов
        similar_recipes = recommender.find_similar_recipes(", ".join(ingredients_list))
        
        if similar_recipes.empty:
            print("Похожие рецепты не найдены.")
        else:
            # Отображаем каждый найденный рецепт
            for _, row in similar_recipes.iterrows():
                title = row.get('title', 'Без названия')
                rating = row.get('rating', 'Рейтинг недоступен')
                url = row.get('url', 'URL недоступен')
                similarity = row.get('similarity_score', 0)
                
                print(f"- {title}")
                print(f"  Рейтинг: {rating}")
                print(f"  Сходство: {similarity:.3f}")
                if 'url' in row:
                    print(f"  Ссылка: {url}")
                print()
                
    except Exception as e:
        print(f"Ошибка поиска похожих рецептов: {e}")

if __name__ == "__main__":
    main()