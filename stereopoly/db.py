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
    return dict(name = self.name, money = self.money)

  def get_translatables(self):
    return [dict(
      id = self.name,
      user_comments = (
        'name for money scheme {0}'.format(self.id),
      )
    )]

  @property
  def money(self):
    m = [self.money1, self.money2, self.money3, self.money4, self.money5, self.money6, self.money7, self.money8, self.money9, self.money10]
    return tuple([c for c in m if c])

class NewsgroupsNews(Base):
  __tablename__ = "newsgroupsnews"
  newsgroup_id = Column(Integer, ForeignKey('newsgroups.id'))
  news_id = Column(Integer, ForeignKey('news.id'))
  __table_args__ = (
    PrimaryKeyConstraint('newsgroup_id', 'news_id'),
  )

class BoardNewsgroups(Base):
  __tablename__ = "boardnewsgroups"
  board_id = Column(Integer, ForeignKey('boards.id'))
  newsgroup_id = Column(Integer, ForeignKey('newsgroups.id'))
  __table_args__ = (
    PrimaryKeyConstraint('board_id', 'newsgroup_id'),
  )

class Newsgroup(Base):
  __tablename__ = "newsgroups"
  id = Column(Integer, nullable = False, primary_key = True)
  name = Column(Unicode, nullable = False)
  news = relationship('News', secondary = "newsgroupsnews", backref = "newsgroups")

class Board(Base):
  __tablename__ = 'boards'
  id = Column(Integer, primary_key=True)
  name = Column(Unicode, unique=True, nullable = False)
  money_scheme = Column(Integer, ForeignKey('money_schemes.id'), nullable = False)
  version = Column(Integer, nullable=False, default = 1)
  start_money = Column(Integer, nullable = False)
  scheme = relationship('MoneyScheme', backref = "boards")
  newsgroups = relationship('Newsgroup', secondary = "boardnewsgroups", backref = "boards")
  chance_cards = relationship('ChanceCard', secondary = "boardchancecards", backref = "boards")
  community_chest_cards = relationship('CommunityChestCard', secondary = "boardcommunitychestcards", backref = "boards")

  def format_cost_percentage(self, o):
    if o['cost_percentage'] > 0:
      fi = string.Formatter().parse(o['text'])
      if len([f for f in fi if f[1] == 'cost']):
        cost = self.start_money * o['cost_percentage']
        mul = cost / self.scheme.money[0]
        mul = max(round(mul), 1)
        cost = self.scheme.money[0] * mul
        o['text'] = o['text'].format(cost = self.scheme.name.format(cost))
    del o['cost_percentage']

  def to_dict(self):
    b = dict(name = self.name, id = self.id, version = self.version, newsgroups = list(), money_scheme = self.scheme.to_dict(), chance_cards = list(), community_chest_cards = list())
    for n in self.newsgroups:
      b['newsgroups'].append(dict(news = list()))
      for nn in n.news:
        nd = nn.to_dict()
        self.format_cost_percentage(nd)
        b['newsgroups'][-1]['news'].append(nd)

    for c in self.chance_cards:
      oc = c.to_dict()
      self.format_cost_percentage(oc)
      b['chance_cards'].append(oc)

    for c in self.community_chest_cards:
      oc = c.to_dict()
      self.format_cost_percentage(oc)
      b['community_chest_cards'].append(oc)

    return b

  def get_translatables(self):
    translatables = list()
    translatables.append(dict(
      id = self.name,
      user_comments = (
        'name of board {0}'.format(self.id),
      )
    ))

    for ng in self.newsgroups:
      for n in ng.news:
        translatables += n.get_translatables()
        
    for c in self.chance_cards:
      translatables += c.get_translatables()
    for c in self.community_chest_cards:
      translatables += c.get_translatables()
    translatables += self.scheme.get_translatables()
    return translatables

class News(Base):
  __tablename__ = "news"
  id = Column(Integer, primary_key=True)
  text = Column(Unicode, nullable = False)
  version = Column(Integer, nullable = False, default = 1)
  cost_percentage = Column(Float, default=0.0)

  def to_dict(self):
    return dict(text = self.text, cost_percentage = self.cost_percentage)

  def get_translatables(self):
    return [dict(
      id = self.text,
      user_comments = (
        'text of news {0}'.format(self.id),
      )
    )]

class ChanceCard(Base):
  __tablename__ = "chance_cards"
  id = Column(Integer, primary_key=True)
  text = Column(Unicode, nullable = False)
  version = Column(Integer, nullable = False, default = 1)
  cost_percentage = Column(Float, default=0.0)

  def to_dict(self):
    return dict(text = self.text, cost_percentage = self.cost_percentage)

  def get_translatables(self):
    return [dict(
      id = self.text,
      user_comments = (
        'text of chance card {0}'.format(self.id),
      )
    )]

class CommunityChestCard(Base):
  __tablename__ = "community_chest_cards"
  id = Column(Integer, primary_key=True)
  text = Column(Unicode, nullable = False)
  version = Column(Integer, nullable = False, default = 1)
  cost_percentage = Column(Float, default=0.0)

  def to_dict(self):
    return dict(text = self.text, cost_percentage = self.cost_percentage)

  def get_translatables(self):
    return [dict(
      id = self.text,
      user_comments = (
        'text of community chest card {0}'.format(self.id),
      )
    )]

class BoardChanceCards(Base):
  __tablename__ = "boardchancecards"
  board_id = Column(Integer, ForeignKey('boards.id'))
  chance_card_id = Column(Integer, ForeignKey('chance_cards.id'))
  __table_args__ = (
    PrimaryKeyConstraint('board_id', 'chance_card_id'),
  )

class BoardCommunityChestCards(Base):
  __tablename__ = "boardcommunitychestcards"
  board_id = Column(Integer, ForeignKey('boards.id'))
  community_chest_card_id = Column(Integer, ForeignKey('community_chest_cards.id'))
  __table_args__ = (
    PrimaryKeyConstraint('board_id', 'community_chest_card_id'),
  )

def setup():
  global Base
  engine = create_engine('sqlite:///stereopoly.db')
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all()
  return Session
