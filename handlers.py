import os
import re
from datetime import datetime
from weather.engine import WeatherMaker, DatabaseUpdater, ImageMaker
from config import PATH_TO_SAVE_CARDS


def check_date_from(text, context):
    re_date = re.compile(r'\d+-\d+-\d{4}')
    date_from = re_date.findall(text)
    if date_from:
        context['date_from'] = date_from[0]
        return True
    return False


def check_date_to(text, context):
    re_date = re.compile(r'\d+-\d+-\d{4}')
    date_to = re_date.findall(text)
    if date_to:
        context['date_to'] = date_to[0]
        return True
    return False


def add_forecasts_to_db(text, context):
    date_from = datetime.strptime(context["date_from"], "%d-%m-%Y")
    date_to = datetime.strptime(context["date_to"], "%d-%m-%Y")
    weather_maker = WeatherMaker()
    weather_maker.pull_weather_data(date_from, date_to)
    forecasts = weather_maker.get_weather_data()
    if forecasts:
        print(f"Получено {len(forecasts)} новых элементов")
    else:
        print(f"[X] Не удалось получить данные за выбранный период")
    database_updater = DatabaseUpdater("sqlite:///forecasts.db")
    database_updater.save_forecasts(forecasts)
    return True


def get_forecasts_from_db(text, context):
    database_updater = DatabaseUpdater("sqlite:///forecasts.db")
    date_from = datetime.strptime(context["date_from"], "%d-%m-%Y")
    date_to = datetime.strptime(context["date_to"], "%d-%m-%Y")
    forecasts = database_updater.get_forecasts(date_from, date_to)
    if forecasts:
        print(f"Получено из базы данных {len(forecasts)} записей")
    else:
        print(f"[X] Не удалось найти прогнозы за выбранный период")
    context['forecasts'] = forecasts
    return True


def print_forecasts(text, context):
    forecasts = context.get('forecasts', None)
    if forecasts:
        for forecast in forecasts:
            forecast_date = forecast["date"].strftime("%d-%m-%Y")
            print(forecast_date, forecast["weather_type"], forecast["temperature"])
    else:
        print("Для продолжения необходимо получить из базы хотябы один прогноз")

    return True


def select_forecast_to_card_create(text, context):
    forecasts = context.get('forecasts', None)
    if forecasts:
        for index, forecast in enumerate(forecasts):
            forecast_date = forecast["date"].strftime("%d-%m-%Y")
            print(f"{index + 1}: {forecast_date} {forecast['weather_type']} {forecast['temperature']}")
        user_choose = input(">>> ")
        if user_choose.isdigit() and (int(user_choose) - 1) in range(len(forecasts)):
            selected_forecast = forecasts[int(user_choose) - 1]
            image_maker = ImageMaker(selected_forecast)
            print("Создаем открытку. Пожалуйста подождите...")
            image_maker.create_card()
            new_card_name = selected_forecast["date"].strftime("%d-%m-%Y") + ".jpg"
            path_to_card = os.path.join(PATH_TO_SAVE_CARDS, new_card_name)
            image_maker.save_card(path_to_card)
            print("Открытка была сохранена. Результат будет выведен на экран через несколько секунд...")
            image_maker.view_card()
            return True
    else:
        print("Для продолжения необходимо получить из базы хотябы один прогноз")
        return True
