from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Unicode, Integer, Float, func, ForeignKey, Index, collate, Boolean, UniqueConstraint
from sqlalchemy import PrimaryKeyConstraint

import string

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

  def to_dict(self):
    return dict(name = self.name, id = self.id, money = self.money)

  @property
  def money(self):
    m = [self.money1, self.money2, self.money3, self.money4, self.money5, self.money6, self.money7, self.money8, self.money9, self.money10]
    return tuple([c for c in m if c])

class Boardnews(Base):
  __tablename__ = "boardnews"
  board_id = Column(Integer, ForeignKey('boards.id'))
  news_id = Column(Integer, ForeignKey('news.id'))
  __table_args__ = (
    PrimaryKeyConstraint('board_id', 'news_id'),
  )

class Board(Base):
  __tablename__ = 'boards'
  id = Column(Integer, primary_key=True)
  name = Column(Unicode, unique=True, nullable = False)
  money_scheme = Column(Integer, ForeignKey('money_schemes.id'), nullable = False)
  version = Column(Integer, nullable=False, default = 1)
  start_money = Column(Integer, nullable = False)
  scheme = relationship('MoneyScheme', backref = "boards")
  news = relationship('News', secondary = "boardnews", backref = "boards")

  def format_news(self, n):
    if n['cost_percentage'] > 0:
      fi = string.Formatter().parse(n['text'])
      if len([f for f in fi if f[1] == 'cost']):
        cost = self.start_money * n['cost_percentage']
        mul = cost / self.scheme.money[0]
        mul = max(round(mul), 1)
        cost = self.scheme.money[0] * mul
        n['text'] = n['text'].format(cost = self.scheme.name.format(cost))
    del n['cost_percentage']

  def to_dict(self):
    b = dict(name = self.name, id = self.id, version = self.version, news = list(), money_scheme = self.scheme.to_dict())
    for n in self.news:
      nd = n.to_dict()
      self.format_news(nd)
      b['news'].append(nd)
    return b

class News(Base):
  __tablename__ = "news"
  id = Column(Integer, primary_key=True)
  text = Column(Unicode, nullable = False)
  version = Column(Integer, nullable = False, default = 1)
  cost_percentage = Column(Float, default=0.0)

  def to_dict(self):
    return dict(text = self.text, id = self.id, cost_percentage = self.cost_percentage)

def setup():
  global Base
  engine = create_engine('sqlite:///stereopoly.db')
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all()
  return Session
