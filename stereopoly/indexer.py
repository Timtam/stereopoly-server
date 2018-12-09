from yaml import load as yaml_load
try:
  from yaml import CLoader as yaml_loader
except ImportError:
  from yaml import Loader as yaml_loader

from stereopoly.config import CHANCE_CARDS_FILE, COMMUNITY_CHEST_CARDS_FILE, NEWS_FILE, MONEY_SCHEMES_FILE, BOARDS_FILE, NEWSGROUPS_FILE
from stereopoly.db import News, MoneyScheme, Board, Newsgroup, NewsgroupsNews, BoardNewsgroups, BoardChanceCards, BoardCommunityChestCards, ChanceCard, CommunityChestCard
from stereopoly import globals

class Indexer(object):
  def __init__(self):
    self.__boards = dict()
    self.__chance_cards = dict()
    self.__community_chest_cards = dict()
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

    for news_id in self.__news:
      news = self.__news[news_id]
      news['id'] = news_id
      print("Indexing news (id={0})".format(news_id))
      self.index_news(news, session)

    for chance_id in self.__chance_cards:
      card = self.__chance_cards[chance_id]
      card['id'] = chance_id
      print("Indexing chance card (id={0})".format(chance_id))
      self.index_chance_card(card, session)

    for community_id in self.__community_chest_cards:
      card = self.__community_chest_cards[community_id]
      card['id'] = community_id
      print("Indexing community chest card (id={0})".format(community_id))
      self.index_community_chest_card(card, session)

    for newsgroup_id in self.__newsgroups:
      self.__newsgroups[newsgroup_id]['id'] = newsgroup_id
      newsgroup = dict(self.__newsgroups[newsgroup_id])
      print("Indexing newsgroup (id={0})".format(newsgroup_id))
      self.index_newsgroup(newsgroup, session)

    for board_id in self.__boards:
      self.__boards[board_id]['id'] = board_id
      board = dict(self.__boards[board_id])
      print("Indexing board '{0}' (id={1})".format(board['name'], board_id))
      self.index_board(board, session)

    self.cleanup(session)

    session.commit()

  def load_files(self):
    with open(CHANCE_CARDS_FILE, "r") as f:
      self.__chance_cards = yaml_load(f, Loader=yaml_loader)
    with open(COMMUNITY_CHEST_CARDS_FILE, "r") as f:
      self.__community_chest_cards = yaml_load(f, Loader=yaml_loader)
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
      if not self.__newsgroups[n_id].get('changed', False) and conn:
        continue
      changed = True
      if not conn:
        print("Adding newsgroup '{0}' (id={1}) to board '{2}' (id={3}).".format(self.__newsgroups[n_id]['name'], n_id, board['name'], board['id']))
        session.add(BoardNewsgroups(board_id = board['id'], newsgroup_id = n_id))
    del board['newsgroups']

    # checking chance cards

    for c_id in board['chance_cards']:
      conn = session.query(BoardChanceCards).filter_by(board_id = board['id'], chance_card_id = c_id).first()
      if not self.__chance_cards[c_id].get('changed', False) and conn:
        continue
      changed = True
      if not conn:
        print("Adding chance card (id={0}) to board '{1}' (id={2}).".format(c_id, board['name'], board['id']))
        session.add(BoardChanceCards(board_id = board['id'], chance_card_id = c_id))
    del board['chance_cards']

    # checking community chest cards

    for c_id in board['community_chest_cards']:
      conn = session.query(BoardCommunityChestCards).filter_by(board_id = board['id'], community_chest_card_id = c_id).first()
      if not self.__community_chest_cards[c_id].get('changed', False) and conn:
        continue
      changed = True
      if not conn:
        print("Adding community chest card (id={0}) to board '{1}' (id={2}).".format(c_id, board['name'], board['id']))
        session.add(BoardCommunityChestCards(board_id = board['id'], community_chest_card_id = c_id))
    del board['community_chest_cards']

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
        print("News text changed, updating...")
        db_news.text = news['text']
        changed = True
      if news.get('cost_percentage', 0.0) != db_news.cost_percentage:
        print("News cost percentage changed, updating...")
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

  def cleanup_relationships(self, session):
    newsgroupsnews = session.query(NewsgroupsNews).all()
    for n in newsgroupsnews:
      r = False
      if n.newsgroup_id not in self.__newsgroups:
        r = True
      else:
        if n.news_id not in self.__newsgroups[n.newsgroup_id]['news']:
          r = True
      if r:
        session.delete(n)

    boardnewsgroups = session.query(BoardNewsgroups).all()
    for b in boardnewsgroups:
      r = False
      if b.board_id not in self.__boards:
        r = True
      else:
        if b.newsgroup_id not in self.__boards[b.board_id]['newsgroups']:
          r = True
      if r:
        session.delete(b)

    boardchancecards = session.query(BoardChanceCards).all()
    for b in boardchancecards:
      r = False
      if b.board_id not in self.__boards:
        r = True
      else:
        if b.chance_card_id not in self.__boards[b.board_id]['chance_cards']:
          r = True
      if r:
        session.delete(b)

    boardcommunitychestcards = session.query(BoardCommunityChestCards).all()
    for b in boardcommunitychestcards:
      r = False
      if b.board_id not in self.__boards:
        r = True
      else:
        if b.community_chest_card_id not in self.__boards[b.board_id]['community_chest_cards']:
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
      
  def cleanup(self, session):
    print("Cleaning up remaining money schemes...")
    schemes = session.query(MoneyScheme).all()
    for scheme in schemes:
      if scheme.id not in self.__money_schemes:
        session.delete(scheme)

    print("Cleaning up remaining news...")
    news = session.query(News).all()
    for n in news:
      if n.id not in self.__news:
        session.delete(n)

    print("Cleaning up remaining chance cards...")
    cards = session.query(ChanceCard).all()
    for c in cards:
      if c.id not in self.__chance_cards:
        session.delete(c)

    print("Cleaning up remaining community chest cards...")
    cards = session.query(CommunityChestCard).all()
    for c in cards:
      if c.id not in self.__community_chest_cards:
        session.delete(c)

    print("Cleaning up remaining newsgroups...")
    newsgroups = session.query(Newsgroup).all()
    for ng in newsgroups:
      if ng.id not in self.__newsgroups:
        session.delete(ng)

    print("Cleaning up remaining boards...")
    boards = session.query(Board).all()
    for board in boards:
      if board.id not in self.__boards:
        session.delete(board)

    print("Cleaning up remaining relationship tables...")
    self.cleanup_relationships(session)

  def index_chance_card(self, card, session):
    changed = False
    db_card = session.query(ChanceCard).filter_by(id = card['id']).first()
    if not db_card:
      session.add(ChanceCard(**card))
      print("New chance card added.")
    else:
      if card['text'] != db_card.text:
        print("Chance card text changed, updating...")
        db_card.text = card['text']
        changed = True
      if card.get('cost_percentage', 0.0) != db_card.cost_percentage:
        print("Chance card cost percentage changed, updating...")
        db_card.cost_percentage = card.get('cost_percentage', 0.0)
        changed = True

      if changed:
        card['changed'] = True
        print("Chance card was changed, increasing version to v{0}".format(db_card.version + 1))
        db_card.version += 1
      else:
        print("No changes detected.")

  def index_community_chest_card(self, card, session):
    changed = False
    db_card = session.query(CommunityChestCard).filter_by(id = card['id']).first()
    if not db_card:
      session.add(CommunityChestCard(**card))
      print("New community chest card added.")
    else:
      if card['text'] != db_card.text:
        print("Community chest card text changed, updating...")
        db_card.text = card['text']
        changed = True
      if card.get('cost_percentage', 0.0) != db_card.cost_percentage:
        print("Community chest card cost percentage changed, updating...")
        db_card.cost_percentage = card.get('cost_percentage', 0.0)
        changed = True

      if changed:
        card['changed'] = True
        print("Community chest card was changed, increasing version to v{0}".format(db_card.version + 1))
        db_card.version += 1
      else:
        print("No changes detected.")
