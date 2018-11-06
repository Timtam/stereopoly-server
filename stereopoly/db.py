from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Unicode, Integer, func, ForeignKey, Index, collate, Boolean, UniqueConstraint
from sqlalchemy import PrimaryKeyConstraint

Base = declarative_base()

class MoneyScheme(Base):
  __tablename__ = 'money_schemes'
  id = Column(Integer, primary_key=True)
  name = Column(Unicode, index=True, unique=True, nullable=False)
  money1 = Column(Integer)
  money2 = Column(Integer)
  money3 = Column(Integer)
  money4 = Column(Integer)
  money5 = Column(Integer)
  money6 = Column(Integer)
  money7 = Column(Integer)
  money8 = Column(Integer)
  money9 = Column(Integer)
  money10 = Column(Integer)

  @property
  def money(self):
    m = [self.money1, self.money2, self.money3, self.money4, self.money5, self.money6, self.money7, self.money8, self.money9, self.money10]
    return tuple([c for c in m if m])

class Board(Base):
  __tablename__ = 'boards'
  id = Column(Integer, primary_key=True)
  name = Column(Unicode, unique=True, nullable = False)
  money_scheme = Column(Integer, ForeignKey('money_schemes.id'), nullable = False)
  version = Column(Integer, nullable=False, default = 1)
  scheme = relationship('MoneyScheme', foreign_keys=[money_scheme])

class News(Base):
  __tablename__ = "news"
  id = Column(Integer, primary_key=True)
  text = Column(Unicode, nullable = False)
  version = Column(Integer, nullable = False, default = 1)

def setup():
  global Base
  engine = create_engine('sqlite:///stereopoly.db')
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all()
  return Session
