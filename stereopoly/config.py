from .path import get_script_directory

import os.path

class Config(object):
  DEBUG = True
  CSRF_ENABLED = True
  JSON_AS_ASCII = False

BOARDS_FILE = os.path.join(get_script_directory(), 'var', 'boards.yml')
MONEY_SCHEMES_FILE = os.path.join(get_script_directory(), "var", "money.yml")
NEWS_FILE = os.path.join(get_script_directory(), "var", "news.yml")
NEWSGROUPS_FILE = os.path.join(get_script_directory(), "var", "newsgroups.yml")
SUPPORTED_APP_VERSION = "1.0.0"