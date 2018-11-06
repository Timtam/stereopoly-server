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

    for board_id in self.__boards:
      board = self.__boards[board_id]
      board['id'] = board_id
      print("Indexing board '{0}' (id={1})".format(board['name'], board_id))
      self.index_board(board)

  def load_files(self):
    with open(NEWS_FILE, "r") as f:
      self.__news = yaml_load(f, Loader=yaml_loader)
    with open(MONEY_SCHEMES_FILE, "r") as f:
      self.__money_schemes = yaml_load(f, Loader=yaml_loader)
    with open(BOARDS_FILE, "r") as f:
      self.__boards = yaml_load(f, Loader=yaml_loader)

  def index_board(self, board):
    pass