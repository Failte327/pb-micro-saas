from sqlalchemy import create_engine, Column, Integer
from sqlalchemy_utils import database_exists, create_database

engine = create_engine("sqlite:///court_pool.db")
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

class AvailableCourts():
    __tablename__ = "available_courts"

    id = Column(Integer, primary_key=True)
    available_courts = Column(Integer)

