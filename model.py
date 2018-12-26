from sqlalchemy import Column, ForeignKey, Integer, Float, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Logfiles(Base):
    """
    Таблица логов
    """
    __tablename__ = 'logfiles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(20) )
    turn = Column(String(20))
    author = Column(String(50))
    area = Column(String(50))
    model = Column(String(50))
    vin = Column(String(50))
    problem = Column(Text())
    reason = Column(Text())
    done_actions = Column(Text())
    how_to_fix = Column(Text())
    ran = Column(String(20))
    part_number_id = Column(String(30))
    part_name = Column(String(30))
    iln = Column(String(20))
    creator = Column(String(40))


    def __repr__(self):
        return '<LogFiles> {}'.format(self.date)


    def __str__(self):
        return '<LogFiles> {}'.format(self.date)


