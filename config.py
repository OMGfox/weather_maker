INTENTS = {
    "1": {
        "name": "Добавление прогнозов за диапазон дат в базу данных",
        "scenario_name": "add_forecasts_to_db",
    },
    "2": {
        "name": "Получение прогнозов за диапазон дат из базы",
        "scenario_name": "get_forecasts_from_db",
    },
    "3": {
        "name": "Создание открытки",
        "scenario_name": "create_card"
    },
    "4": {
        "name": "Вывод прогнозов в консоль",
        "scenario_name": "print_forecasts"
    }
}

SCENARIOS = {
    "add_forecasts_to_db": {
        "step1": {
            "message": "Введите дату начала диапазона. (В формате: 01-12-2020)",
            "failure": "Неверный формат даты, попробуйте еще раз",
            "handler": "check_date_from",
            "input_required": True,
            "next_step": "step2"
        },
        "step2": {
            "message": "Введите дату конца диапазона. (В формате: 01-12-2020)",
            "failure": "Неверный формат даты, попробуйте еще раз",
            "handler": "check_date_to",
            "input_required": True,
            "next_step": "step3"
        },
        "step3": {
            "message": "Получаем новые данные...",
            "failure": None,
            "handler": "add_forecasts_to_db",
            "input_required": False,
            "next_step": None
        }
    },
    "get_forecasts_from_db": {
        "step1": {
            "message": "Введите дату начала диапазона. (В формате: 01-12-2020)",
            "failure": "Неверный формат даты, попробуйте еще раз",
            "handler": "check_date_from",
            "input_required": True,
            "next_step": "step2"
        },
        "step2": {
            "message": "Введите дату конца диапазона. (В формате: 01-12-2020)",
            "failure": "Неверный формат даты, попробуйте еще раз",
            "handler": "check_date_to",
            "input_required": True,
            "next_step": "step3"
        },
        "step3": {
            "message": "Достаем прогнозы из базы данных...",
            "failure": None,
            "handler": "get_forecasts_from_db",
            "input_required": False,
            "next_step": None
        }
    },
    "create_card": {
        "step1": {
            "message": "Выберите прогноз по которому вы хотите создать открытку",
            "failure": "Неверный номер. Попробуйте еще раз",
            "handler": "select_forecast_to_card_create",
            "input_required": False,
            "next_step": None
        }
    },
    "print_forecasts": {
        "step1": {
            "message": "Выводим на экран полученные прогнозы...",
            "failure": None,
            "handler": "print_forecasts",
            "input_required": False,
            "next_step": None
        }
    }
}


PATH_TO_SAVE_CARDS = "saved_cards"
