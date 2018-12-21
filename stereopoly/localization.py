from stereopoly import globals
from stereopoly.config import LANGUAGES_FILE
from stereopoly import db
from stereopoly.path import get_script_directory

from babel.messages import (
  catalog,
  extract,
  mofile,
  pofile
)
import gettext
import natsort
import os
import os.path
import pycountry
import sys
from yaml import load as yaml_load
from yaml import dump as yaml_dump
try:
  from yaml import CLoader as yaml_loader
  from yaml import CDumper as yaml_dumper
except ImportError:
  from yaml import Loader as yaml_loader
  from yaml import Dumper as yaml_dumper

class Language(object):
  code = ''
  id = 0
  name = ''

  def __init__(self, id = 0, name = 'English', code = 'en'):
    self.id = id
    if code and not name:
      self.name = pycountry.languages.get(alpha_2 = code).name
      self.code = code
    elif name and not code:
      self.code = pycountry.languages.get(name = self.name).alpha_2
    elif not name and not code:
      raise ValueError('Either name or code must be provided')
    else:
      self.name = name
      self.code = code

  @property
  def folder(self):
    return os.path.join(get_script_directory(), 'locale', self.code)

  @property
  def po_file(self):
    return os.path.join(self.folder, 'LC_MESSAGES', 'stereopoly.po')

  @property
  def mo_file(self):
    return os.path.join(self.folder, 'LC_MESSAGES', 'stereopoly.mo')

  def to_dict(self):
    return dict(id = self.id, name = self.name, code = self.code)

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
      #locations = (token[0], token[1], ), # currently bricks with 2.6.0
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

def _(string, lang = 0):
  olang = find_language(lang)
  if not olang:
    return gettext.NullTranslations().gettext(string)
  else:
    return gettext.translation(
      'stereopoly',
      os.path.join(get_script_directory(), 'locale'),
      languages = [olang.code],
      fallback = True
    ).gettext(string)
    
def load_languages():
  globals.LANGUAGES.append(Language())
  if os.path.exists(LANGUAGES_FILE):
    with open(LANGUAGES_FILE, 'r') as f:
      langs = yaml_load(f, Loader = yaml_loader)
      for id in langs.keys():
        l = langs[id]
        globals.LANGUAGES.append(Language(id = id, name = l['name'], code = l['code']))
  # injecting into global namespace
  sys.modules['builtins'].__dict__['_'] = _

def add_new_language(lang):
  langname = ''
  langcode = ''
  if not lang.isalpha():
    print("Language may only be alphabetic.")
    return
  if len(lang) == 2:
    print("Got two-letter alphabetic name, expecting to be language code")
    lang = pycountry.languages.get(alpha_2 = lang)
    if not lang:
      print("No language found with that code.")
      return
  else:
    print("Language is longer than two signs, therefore seems to be fully qualified language")
    lang = pycountry.languages.get(name = lang)
    if not lang:
      print("No language found with that name")
      return
  langname = lang.name
  langcode = lang.alpha_2
  new_id = natsort.natsorted(globals.LANGUAGES, key = lambda l: l.id)[-1].id + 1
  
  print("Creating language {0} ({1}) with id {2}".format(langname, langcode, new_id))

  globals.LANGUAGES.append(Language(id = new_id, name = langname, code = langcode))

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
    d = l.to_dict()
    langs[d['id']] = d
    del d['id']
  data = yaml_dump(langs, Dumper = yaml_dumper, default_flow_style = False)
  with open(LANGUAGES_FILE, 'w') as f:
    f.write(data)

  print("Done.")

def find_language(lang):
  for l in globals.LANGUAGES[1:]:
    if (isinstance(lang, int) and l.id == lang) or \
       (not isinstance(lang, int) and l.name.lower() == lang.lower() or l.code.lower() == lang.lower()):
      return l
  return None

def language_exists(lang):
  return find_language(lang) is not None

def update_language(lang):

  olang = find_language(lang)
  print("Updating language {0} ({1})".format(olang.name, olang.code))

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

def compile_message_catalog(lang):

  olang = find_language(lang)

  if not olang:
    print("No language with that name found.")
    return

  if not os.path.exists(olang.po_file):
    print("No po file found for language {0}".format(olang.name))
    return

  print("Compiling catalog for language {0}".format(olang.name))

  print("Reading file {0}".format(olang.po_file))
  with open(olang.po_file, 'r') as f:
    cat = pofile.read_po(f)

  print("Writing file {0}".format(olang.mo_file))
  with open(olang.mo_file, 'wb') as f:
    mofile.write_mo(f, cat)
  print("Done.")