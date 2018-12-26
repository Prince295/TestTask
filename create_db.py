from sqlalchemy import create_engine

from model import Base
from settings import DATABASE_URL


def create_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

create_db()
