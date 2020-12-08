# -*- coding: utf-8 -*-

# В очередной спешке, проверив приложение с прогнозом погоды, вы выбежали
# навстречу ревью вашего кода, которое ожидало вас в офисе.
# И тут же день стал хуже - вместо обещанной облачности вас встретил ливень.

# Вы промокли, настроение было испорчено, и на ревью вы уже пришли не в духе.
# В итоге такого сокрушительного дня вы решили написать свою программу для прогноза погоды
# из источника, которому вы доверяете.

# Для этого вам нужно:

# Создать модуль-движок с классом WeatherMaker, необходимым для получения и формирования предсказаний.
# В нём должен быть метод, получающий прогноз с выбранного вами сайта (парсинг + re) за некоторый диапазон дат,
# а затем, получив данные, сформировать их в словарь {погода: Облачная, температура: 10, дата:datetime...}

# Добавить класс ImageMaker.
# Снабдить его методом рисования открытки
# (использовать OpenCV, в качестве заготовки брать lesson_016/python_snippets/external_data/probe.jpg):
#   С текстом, состоящим из полученных данных (пригодится cv2.putText)
#   С изображением, соответствующим типу погоды
# (хранятся в lesson_016/python_snippets/external_data/weather_img ,но можно нарисовать/добавить свои)
#   В качестве фона добавить градиент цвета, отражающего тип погоды
# Солнечно - от желтого к белому
# Дождь - от синего к белому
# Снег - от голубого к белому
# Облачно - от серого к белому

# Добавить класс DatabaseUpdater с методами:
#   Получающим данные из базы данных за указанный диапазон дат.
#   Сохраняющим прогнозы в базу данных (использовать peewee)

# Сделать программу с консольным интерфейсом, постаравшись все выполняемые действия вынести в отдельные функции.
# Среди действий, доступных пользователю, должны быть:
#   Добавление прогнозов за диапазон дат в базу данных
#   Получение прогнозов за диапазон дат из базы
#   Создание открыток из полученных прогнозов
#   Выведение полученных прогнозов на консоль
# При старте консольная утилита должна загружать прогнозы за прошедшую неделю.

# Рекомендации:
# Можно создать отдельный модуль для инициализирования базы данных.
# Как далее использовать эту базу данных в движке:
# Передавать DatabaseUpdater url-путь
# https://peewee.readthedocs.io/en/latest/peewee/playhouse.html#db-url
# Приконнектится по полученному url-пути к базе данных
# Инициализировать её через DatabaseProxy()
# https://peewee.readthedocs.io/en/latest/peewee/database.html#dynamically-defining-a-database

from config import INTENTS, SCENARIOS
from weather.engine import WeatherMaker, DatabaseUpdater
import handlers
from datetime import datetime, timedelta


class UserState:
    """
    class to keep context to exchange between handlers, and current scenario step
    """
    def __init__(self):
        self.scenario_name = None
        self.step = None
        self.context = {}


def available_intents() -> str:
    """
    return string with available intents from config.INTENTS
    @return: str
    """
    result = '\n'
    for key, intent in INTENTS.items():
        result += f"{key}: {intent['name']}\n"
    result += "0: Выход\n>>> "
    return result


def loading_data_by_last_week():
    print("Пожалуйста подождите. Пополняем базу данных данными за последние 7 дней")
    date_now = datetime.now()
    date_from = date_now - timedelta(days=7)
    database_updater = DatabaseUpdater("sqlite:///forecasts.db")
    weather_maker = WeatherMaker()
    weather_maker.pull_weather_data(date_from, date_now)
    forecasts = weather_maker.get_weather_data()
    forecasts_already_in_db = database_updater.get_forecasts(date_from, date_now)
    database_updater.save_forecasts(forecasts)
    print(f"Было обнаружено и записано {len(forecasts) - len(forecasts_already_in_db)} новых прогнозов")


if __name__ == '__main__':
    loading_data_by_last_week()
    user_state = UserState()
    is_stopped = False
    while not is_stopped:
        if user_state.scenario_name is None:
            intents = available_intents()
            user_choose = input(intents)
            if user_choose == '0':
                is_stopped = True
            elif user_choose in INTENTS:
                user_state.scenario_name = INTENTS[user_choose]['scenario_name']
                user_state.step_name = 'step1'
            else:
                print(f'Элемент с номером "{user_choose}" не найден! Попробуйте еще раз.\n')
        else:
            current_step = SCENARIOS[user_state.scenario_name][user_state.step_name]
            handler_name = current_step['handler']
            message = current_step['message']
            handler = getattr(handlers, handler_name)
            if current_step['input_required']:
                user_input = input(message + "\n>>> ")
            else:
                user_input = None
            result = handler(user_input, user_state.context)
            if result:
                next_step = current_step['next_step']
                if next_step:
                    user_state.step_name = next_step
                else:
                    user_state.scenario_name = None
                    user_state.step_name = None
                continue

            failure_message = current_step['failure']
            print(failure_message)


# зачет!
