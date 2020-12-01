from peewee import DatabaseProxy, Model, CharField, DateTimeField
from playhouse.db_url import connect

database_proxy = DatabaseProxy()  # Create a proxy for our db.


class BaseModel(Model):
    class Meta:
        database = database_proxy  # Use proxy for our DB.


class Forecast(BaseModel):
    weather_type = CharField()
    temperature = CharField()
    date = DateTimeField()


def init_db(url):
    """
    The function to dynamic initialization of the database depending on the transmitted url
    ex.:
    - sqlite:///my_database.db will create a SqliteDatabase
    - postgresql://postgres:my_password@localhost:5432/my_database will create a PostgresqlDatabase instance.
    - mysql://user:passwd@ip:port/my_db will create a MySQLDatabase
    @param url: str
    @return:None
    """
    database = connect(url)
    database_proxy.initialize(database)
    database_proxy.create_tables([Forecast])
