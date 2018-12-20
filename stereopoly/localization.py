from stereopoly import globals
from stereopoly.path import get_script_directory

from babel.messages import (
  catalog,
  extract
)
import gettext
import natsort
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
    return os.path.join(get_script_directory(), 'locale', this.name.lower())

  def to_dict(self):
    return dict(id = self.id, name = self.name)

def get_translation_catalog():
  catalog = catalog.Catalog(fuzzy = False, charset = 'utf-8')
  # we need to retrieve all translatable strings within the source
  tokens = extract.extract_from_dir(
    dirname = os.path.join(get_script_directory(), 'stereopoly'),
  )

  for token in tokens:
    catalog.add(
      token[2],
      locations = (token[0], token[1], ),
      user_comments = token[3],
      context = token[4]
    )
  return catalog

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
  if os.path.exists(os.path.join(get_script_directory(), 'var', 'languages.yml')):
    with open(os.path.join(get_script_directory(), 'var', 'languages.yml'), 'r') as f:
      langs = yaml_load(f, Loader = yaml_loader)
      for id, l in langs:
        globals.LANGUAGES.append(Language(id, l))

def add_new_language(lang):
  new_id = natsort.natsorted(globals.LANGUAGES, key = lambda l: l.id)[-1].id + 1
  
  globals.LANGUAGES.append(Language(new_id, lang))

  if len(globals.LANGUAGES):
    langs = dict()
    for l in globals.LANGUAGES[1:]:
      langs[l.id] = l.name
    data = yaml_dump(langs, Dumper = yaml_dumper)
    with open(os.path.join(get_script_directory(), 'var', 'languages.yml'), 'w') as f:
      f.write(data)

def language_exists(lang):
  return lang in [l.name.lower() for l in globals.LANGUAGES]
