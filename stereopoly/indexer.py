from yaml import load as yaml_load
try:
  from yaml import CLoader as yaml_loader
except ImportError:
  from yaml import Loader as yaml_loader

from stereopoly.config import NEWS_FILE, MONEY_SCHEMES_FILE, BOARDS_FILE, NEWSGROUPS_FILE
from stereopoly.db import News, MoneyScheme, Board, Newsgroup, NewsgroupsNews, BoardNewsgroups
from stereopoly import globals

class Indexer(object):
  def __init__(self):
    self.__boards = dict()
    self.__money_schemes = dict()
    self.__news = dict()
    self.__newsgroups = dict()

  def run(self, session):

    self.load_files()

    for scheme_id in self.__money_schemes:
      scheme = self.__money_schemes[scheme_id]
      scheme['id'] = scheme_id
      print("Indexing money scheme (id={0})".format(scheme_id))
      self.index_money_scheme(scheme, session)

    print("Cleaning up remaining money schemes...")
    schemes = session.query(MoneyScheme).all()
    for scheme in schemes:
      if scheme.id not in self.__money_schemes:
        session.delete(scheme)

    for news_id in self.__news:
      news = self.__news[news_id]
      news['id'] = news_id
      print("Indexing news (id={0})".format(news_id))
      self.index_news(news, session)

    print("Cleaning up remaining news...")
    news = session.query(News).all()
    for n in news:
      if n.id not in self.__news:
        session.delete(n)

    for newsgroup_id in self.__newsgroups:
      newsgroup = self.__newsgroups[newsgroup_id]
      newsgroup['id'] = newsgroup_id
      print("Indexing newsgroup (id={0})".format(newsgroup_id))
      self.index_newsgroup(newsgroup, session)

    for board_id in self.__boards:
      self.__boards[board_id]['id'] = board_id
      board = dict(self.__boards[board_id])
      print("Indexing board '{0}' (id={1})".format(board['name'], board_id))
      self.index_board(board, session)

    print("Cleaning up remaining boards...")
    boards = session.query(Board).all()
    for board in boards:
      if board.id not in self.__boards:
        session.delete(board)

    #print("Cleaning up remaining board-news-relationships...")
    #self.clean_boardnews(session)

    session.commit()

  def load_files(self):
    with open(NEWS_FILE, "r") as f:
      self.__news = yaml_load(f, Loader=yaml_loader)
    with open(MONEY_SCHEMES_FILE, "r") as f:
      self.__money_schemes = yaml_load(f, Loader=yaml_loader)
    with open(BOARDS_FILE, "r") as f:
      self.__boards = yaml_load(f, Loader=yaml_loader)
    with open(NEWSGROUPS_FILE, "r") as f:
      self.__newsgroups = yaml_load(f, Loader=yaml_loader)

  def index_board(self, board, session):
    changed = False
    # checking newsgroups first
    for n_id in board['newsgroups']:
      conn = session.query(BoardNewsgroups).filter_by(board_id = board['id'], newsgroup_id = n_id).first()
      if self.__newsgroups[n_id].get('changed', False) and conn:
        changed = True
      if not conn:
        print("Adding newsgroup '{0}' (id={1}) to board '{2}' (id={3}).".format(self.__newsgroups[n_id]['name'], n_id, board['name'], board['id']))
        session.add(BoardNewsgroups(board_id = board['id'], newsgroup_id = n_id))
    del board['newsgroups']
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
      if db_board.start_money != board['start_money']:
        print("Board start money changed, updating.")
        changed = True
        db_board.start_money = board['start_money']
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
      if news.get('cost_percentage', 0.0) != db_news.cost_percentage:
        print("News cost percentage changed, updating text.")
        db_news.cost_percentage = news.get('cost_percentage', 0.0)
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

  def clean_boardnews(self, session):
    r = False
    boardnews = session.query(Boardnews).all()
    for b in boardnews:
      r = False
      if b.board_id not in self.__boards:
        r = True
      else:
        if b.news_id not in self.__boards[b.board_id]['news']:
          r = True
      if r:
        session.delete(b)

  def index_newsgroup(self, newsgroup, session):
    changed = False

    for n_id in newsgroup['news']:
      conn = session.query(NewsgroupsNews).filter_by(newsgroup_id = newsgroup['id'], news_id = n_id).first()
      if self.__news[n_id].get('changed', False) and conn:
        changed = True
      if not conn:
        print("Adding news (id={0}) to  newsgroup '{1}' (id={2}).".format(n_id, newsgroup['name'], newsgroup['id']))
        session.add(NewsgroupsNews(newsgroup_id = newsgroup['id'], news_id = n_id))
    del newsgroup['news']

    db_newsgroup = session.query(Newsgroup).filter_by(id = newsgroup['id']).first()

    if not db_newsgroup:
      session.add(Newsgroup(**newsgroup))
      print("New newsgroup added.")
    else:
      newsgroup['changed'] = changed