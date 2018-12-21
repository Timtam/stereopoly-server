from stereopoly import globals
from stereopoly.config import LANGUAGES_FILE
from stereopoly import db
from stereopoly.path import get_script_directory

from babel.messages import (
  catalog,
  extract,
  pofile
)
import gettext
import natsort
import os
import os.path
from yaml import load as yaml_load
from yaml import dump as yaml_dump
try:
  from yaml import CLoader as yaml_loader
  from yaml import CDumper as yaml_dumper
except ImportError:
  from yaml import Loader as yaml_loader
  from yaml import Dumper as yaml_dumper

class Language(object):
  id = 0
  name = ''

  def __init__(self, id = 0, name = 'English'):
    self.id = id
    self.name = name

  @property
  def folder(self):
    return os.path.join(get_script_directory(), 'locale', self.name.lower())

  @property
  def po_file(self):
    return os.path.join(self.folder, 'LC_MESSAGES', 'stereopoly.po')

  def to_dict(self):
    return dict(id = self.id, name = self.name)

def get_message_catalog():
  cat = catalog.Catalog(fuzzy = False, charset = 'utf-8')
  # we need to retrieve all translatable strings within the source
  print("Parsing source for translatable strings...")
  tokens = extract.extract_from_dir(
    dirname = os.path.join(get_script_directory(), 'stereopoly'),
  )

  for token in tokens:
    cat.add(
      token[2],
      locations = (token[0], token[1], ),
      user_comments = token[3],
      context = token[4]
    )

  print("Getting translatable strings from database...")

  session = db.setup()()
  boards = session.query(db.Board).all()

  for b in boards:
    for t in b.get_translatables():
      cat.add(
        t['id'],
        user_comments = t['user_comments']
      )
  session.close()

  return cat

def _(string, lang = None):
  if lang is None:
    return gettext.NullTranslations().gettext(string)
  else:
    return gettext.translation(
      'stereopoly',
      'locale',
      languages = [lang],
      fallback = True
    ).gettext(string)
    
def load_languages():
  globals.LANGUAGES.append(Language())
  if os.path.exists(LANGUAGES_FILE):
    with open(LANGUAGES_FILE, 'r') as f:
      langs = yaml_load(f, Loader = yaml_loader)
      for id in langs.keys():
        l = langs[id]
        globals.LANGUAGES.append(Language(id, l))

def add_new_language(lang):
  lang = lang[0].upper() + lang[1:].lower()
  new_id = natsort.natsorted(globals.LANGUAGES, key = lambda l: l.id)[-1].id + 1
  
  print("Creating language with id {0}".format(new_id))

  globals.LANGUAGES.append(Language(new_id, lang))

  # creating folder structure
  lc_folder = os.path.join(globals.LANGUAGES[-1].folder, 'LC_MESSAGES')
  if os.path.exists(lc_folder):
    print("Folder {0} already exists".format(lc_folder))
  else:
    print("Creating folder {0}".format(lc_folder))
    os.makedirs(lc_folder)

  print("Retrieving message catalog...")

  cat = get_message_catalog()

  po_file = globals.LANGUAGES[-1].po_file
  print("Writing file {0}".format(po_file))

  with open(po_file, 'wb') as f:
    pofile.write_po(f, cat)

  print("Writing file {0}".format(LANGUAGES_FILE))

  langs = dict()
  for l in globals.LANGUAGES[1:]:
    langs[l.id] = l.name
  data = yaml_dump(langs, Dumper = yaml_dumper, default_flow_style = False)
  with open(LANGUAGES_FILE, 'w') as f:
    f.write(data)

  print("Done.")

def language_exists(lang):
  return lang in [l.name.lower() for l in globals.LANGUAGES]

def update_language(lang):

  olang = [l for l in globals.LANGUAGES if l.name.lower() == lang][0]
  print("Updating language {0}".format(olang.name))

  print("Retrieving message catalog...")
  
  cat = get_message_catalog()

  if not os.path.exists(olang.po_file):
    print("No po file found.")
  else:
    print("Reading existing file {0}".format(olang.po_file))
    with open(olang.po_file, 'r') as f:
      ocat = pofile.read_po(f)
    ocat.update(cat)
    cat = ocat

  print("Writing {0}".format(olang.po_file))
  with open(olang.po_file, 'wb') as f:
    pofile.write_po(f, cat)

  print("Done.")
