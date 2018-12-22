from stereopoly import globals
from stereopoly.utils import check_app_version

import natsort

@check_app_version
def get_all(api):
  langs = list()
  for l in natsort.natsorted(globals.LANGUAGES, key = lambda l: l.name):
    langs.append(l.to_dict())
  return langs