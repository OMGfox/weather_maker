import re
from calendar import monthrange
from datetime import date, datetime
import locale
import requests
from bs4 import BeautifulSoup
from cv2 import cv2
from db.models import init_db, Forecast


class WeatherMaker:
    """
    class to parse the weather data from html sites
    """
    def __init__(self):
        self.weather_data = list()
        self.date_from = None
        self.date_to = None

    def get_weather_data(self):
        return self.weather_data

    def pull_weather_data(self, date_from: datetime, date_to: datetime):
        """
        main method to pull the weather data by a range of dates
        @param date_from: start of data range
        @param date_to: end of data range
        @return: None
        """
        self.date_from = date_from
        self.date_to = date_to
        current_date = date(year=date_from.year, month=date_from.month, day=1)
        last_date = date(year=date_to.year, month=date_to.month, day=1)
        while current_date.year <= last_date.year and current_date.month <= last_date.month:
            self._parse_weather_data(current_date)
            current_date = self.add_months(current_date, 1)
        self._parse_weather_data_today()

    def _parse_weather_data_today(self):
        """
        method for parsing weather data for this day
        @return: None
        """
        url = f"https://www.gismeteo.ru/weather-sankt-peterburg-4079/"
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'}
        http_response = requests.get(url=url, headers=headers).text
        soup = BeautifulSoup(http_response, 'html.parser')
        weather_frame = soup.find("div", {"class": "tab tooltip"})
        weather_type = self._parse_weather_type(weather_text_description=weather_frame["data-text"])
        temperature = weather_frame.find_all("span", {"class": "unit unit_temperature_c"})[1].text
        date_now = datetime.now()
        forecast_date = datetime(year=date_now.year, month=date_now.month, day=date_now.day)
        self.weather_data.append({"weather_type": weather_type,
                                  "temperature": temperature,
                                  "date": forecast_date})

    def _parse_weather_data(self, date_to_parse: datetime):
        url = f"https://www.gismeteo.ru/diary/4079/{date_to_parse.year}/{date_to_parse.month}/"
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'}
        http_response = requests.get(url=url, headers=headers).text
        soup = BeautifulSoup(http_response, 'html.parser')
        table_rows = soup.find_all('td')
        index = 0
        while index < len(table_rows):
            day = table_rows.__getitem__(index).text
            temperature = table_rows.__getitem__(index + 1).text
            try:
                src = table_rows.__getitem__(index + 4).img.get('src')
            except AttributeError:
                src = table_rows.__getitem__(index + 3).img.get('src')
            weather_type = self._parse_weather_type(src)
            forecast_date = datetime(year=date_to_parse.year, month=date_to_parse.month, day=int(day))
            if self.date_from <= forecast_date <= self.date_to:
                self.weather_data.append({
                    "weather_type": weather_type,
                    "temperature": temperature,
                    "date": forecast_date
                })
            index += 11

    def _parse_weather_type(self, src: str = None, weather_text_description: str = None):
        if src:
            re_file_name = re.compile(r'/(\w+).png')
            file_name = re_file_name.findall(src)[0]
            weather_type_by_src = {
                'sun': "Солнечно",
                'sunc': "Облачно",
                'suncl': "Облачно",
                'dull': "Пасмурно",
                "rain": "Дождь",
                "snow": "Снег",
                "storm": "Гроза"
            }
            return weather_type_by_src[file_name]
        elif weather_text_description:
            weather_text_description = weather_text_description.lower()
            weather_type = {
                "пасмурно": "Пасмурно",
                "солн": "Солнечно",
                "дождь": "Дождь",
                "снег": "Снег",
                "облачно": "Облачно",
                "гроза": "Гроза"
            }
            for key in weather_type:
                if key in weather_text_description:
                    return weather_type[key]

    def add_months(self, source_date, months):
        """
        method to add months to source date
        @param source_date: date
        @param months: int
        @return: new date
        """
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = min(source_date.day, monthrange(year, month)[1])
        return date(year, month, day)


class ImageMaker:
    """
    class to create and save weather cards
    """
    def __init__(self, forecast=None):
        self.path_to_background = 'images/probe.jpg'
        self.forecast = forecast
        self.card = None

    def set_forecast(self, forecast):
        self.forecast = forecast

    def create_card(self):
        """
        The method to start creating
        @return: None
        """
        self.card = cv2.imread(self.path_to_background)
        self._draw_gradient()
        self._draw_weather_icon()
        self._draw_text()

    def save_card(self, path_to_file):
        cv2.imwrite(path_to_file, self.card)

    def view_card(self):
        """
        The method to show the created image
        @return: None
        """
        name_of_window = "The card viewer"
        cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
        cv2.imshow(name_of_window, self.card)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _draw_gradient(self):
        weather_type = self.forecast["weather_type"]
        for row_number, pixels_row in enumerate(self.card):
            for pixel in pixels_row:
                if weather_type == "Солнечно":
                    pixel[0] = row_number
                elif weather_type == "Дождь":
                    pixel[1] = row_number
                    pixel[2] = row_number
                elif weather_type in ("Пасмурно", "Облачно", "Гроза"):
                    pixel[0] = row_number
                    pixel[1] = row_number
                    pixel[2] = row_number
                elif weather_type == "Снег":
                    pixel[2] = row_number

    def _draw_weather_icon(self):
        """
        draw weather icon depended of weather type
        @return: None
        """
        icons = {
            "Солнечно": "images/sun.jpg",
            "Дождь": "images/rain.jpg",
            "Снег": "images/snow.jpg",
            "Пасмурно": "images/cloud.jpg",
            "Облачно": "images/cloud.jpg",
            "Гроза": "images/cloud.jpg",
        }
        background = cv2.imread('images/probe.jpg')
        weather_icon = cv2.imread(icons[self.forecast["weather_type"]])
        background[75: 175, 75: 175] = weather_icon
        self.card = cv2.addWeighted(background, 0.7, self.card, 0.3, 0)

    def _draw_text(self):
        """
        draw a text information from the forecast
        @return:
        """
        locale.setlocale(locale.LC_TIME, ('RU', 'UTF8'))
        date_text = f"{self.forecast['date'].strftime('%d %B %Y')}"
        day_of_week_name = f"{self.forecast['date'].strftime('%A')}"
        weather_text = f"{self.forecast['weather_type']} {self.forecast['temperature']}"
        cv2.putText(self.card, date_text, (250, 100), fontFace=3, fontScale=0.5, color=(0, 0, 0))
        cv2.putText(self.card, day_of_week_name, (250, 120), fontFace=3, fontScale=0.5, color=(0, 0, 0))
        cv2.putText(self.card, weather_text, (250, 140), fontFace=3, fontScale=0.5, color=(0, 0, 0))


class DatabaseUpdater:
    """
    class to save and get forecasts from database
    """
    def __init__(self, url):
        init_db(url)

    def get_forecasts(self, date_from: datetime, date_to: datetime):
        """
        get forecast data from database
        @param date_from: date str "2000-12-01"
        @param date_to: date str "2000-12-01"
        @return: forecast obj
        """
        forecasts = []
        query = Forecast.select().where((date_from <= Forecast.date) & (Forecast.date <= date_to))

        for forecast in query:
            forecasts.append({"weather_type": forecast.weather_type,
                              "temperature": forecast.temperature,
                              "date": forecast.date})
        return forecasts

    def save_forecasts(self, weather_data):
        for data in weather_data:
            Forecast.get_or_create(**data)
