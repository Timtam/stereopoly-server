from .path import get_script_directory

import os.path

class Config(object):
  DEBUG = True
  CSRF_ENABLED = True

NEWS_FILE = os.path.join(get_script_directory(), "var", "news.yml")
SUPPORTED_APP_VERSION = "1.0.0"