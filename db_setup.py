from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import database_exists, create_database

engine = create_engine("sqlite:///auth_token.db")
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

class Base(DeclarativeBase):
    pass

class AuthTokens():
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True)
    auth_token = Column(String(40))
