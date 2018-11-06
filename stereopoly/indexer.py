from yaml import load as yaml_load
try:
  from yaml import CLoader as yaml_loader
except ImportError:
  from yaml import Loader as yaml_loader

from stereopoly.config import NEWS_FILE, MONEY_SCHEMES_FILE, BOARDS_FILE
from stereopoly.db import News, MoneyScheme, Board
from stereopoly import globals

class Indexer(object):
  def __init__(self):
    self.__boards = dict()
    self.__money_schemes = dict()
    self.__news = dict()

  def run(self, session):

    self.load_files()

    for news_id in self.__news:
      news = self.__news[news_id]
      news['id'] = news_id
      print("Indexing news (id={0})".format(news_id))
      self.index_news(news, session)

    for board_id in self.__boards:
      board = self.__boards[board_id]
      board['id'] = board_id
      print("Indexing board '{0}' (id={1})".format(board['name'], board_id))
      self.index_board(board, session)

    session.commit()

  def load_files(self):
    with open(NEWS_FILE, "r") as f:
      self.__news = yaml_load(f, Loader=yaml_loader)
    with open(MONEY_SCHEMES_FILE, "r") as f:
      self.__money_schemes = yaml_load(f, Loader=yaml_loader)
    with open(BOARDS_FILE, "r") as f:
      self.__boards = yaml_load(f, Loader=yaml_loader)

  def index_board(self, board, session):
    pass

  def index_news(self, news, session):
    changed = False
    db_news = session.query(News).filter_by(id = news['id']).first()
    if not db_news:
      session.add(News(**news))
      print("New news added.")
    else:
      if news['text'] != db_news.text:
        print("News text changed, updating text.")
        db_news.text = news['text']
        changed = True
      if changed:
        print("News was changed, increasing version to v{0}".format(db_news.version + 1))
        db_news.version += 1
      else:
        print("No changes detected.")