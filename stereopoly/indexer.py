from yaml import load as yaml_load
try:
  from yaml import CLoader as yaml_loader
except ImportError:
  from yaml import Loader as yaml_loader

from stereopoly.config import NEWS_FILE, MONEY_SCHEMES_FILE, BOARDS_FILE
from stereopoly.db import News, MoneyScheme, Board, Boardnews
from stereopoly import globals

class Indexer(object):
  def __init__(self):
    self.__boards = dict()
    self.__money_schemes = dict()
    self.__news = dict()

  def run(self, session):

    self.load_files()

    for scheme_id in self.__money_schemes:
      scheme = self.__money_schemes[scheme_id]
      scheme['id'] = scheme_id
      print("Indexing money scheme (id={0})".format(scheme_id))
      self.index_money_scheme(scheme, session)

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
    changed = False
    # checking news first
    for n in board['news']:
      conn = session.query(Boardnews).filter_by(board_id = board['id'], news_id = n).first()
      if self.__news[n].get('changed', False) and conn:
        changed = True
      if not conn:
        print("Adding news (id={0}) to board (id={1}).".format(n, board['id']))
        session.add(Boardnews(board_id = board['id'], news_id = n))
    del board['news']
    db_board = session.query(Board).filter_by(id = board['id']).first()
    if not db_board:
      session.add(Board(**board))
      print("New board added.")
    else:
      if db_board.name != board['name']:
        print("Board name changed, updating.")
        changed = True
        db_board.name = board['name']
      if db_board.money_scheme != board['money_scheme']:
        print("Board money scheme changed, updating.")
        changed = True
        db_board.money_scheme = board['money_scheme']
      if changed:
        print("Changes detected, increasing version to v{0}.".format(db_board.version + 1))
        db_board.version += 1
      else:
        print("No changes detected.")

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
        news['changed'] = True
        print("News was changed, increasing version to v{0}".format(db_news.version + 1))
        db_news.version += 1
      else:
        print("No changes detected.")

  def index_money_scheme(self, scheme, session):
    db_scheme = session.query(MoneyScheme).filter_by(id = scheme['id']).first()
    if db_scheme:
      print("Scheme already exists, skipping.")
      return
    session.add(MoneyScheme(**scheme))
    print("Money scheme added.")
