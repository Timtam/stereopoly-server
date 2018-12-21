#!/bin/python

from stereopoly.argument_parser import ArgumentParser
from stereopoly.db import setup as db_setup
from stereopoly import globals
from stereopoly.indexer import Indexer
from stereopoly import localization
from stereopoly.server import setup as server_setup

import sys

def run_indexer():
  # we need an initialized database
  print("Loading database...")
  db = db_setup()
  sess = db()
  print("Running indexer...")
  i = Indexer()
  i.run(sess)
  sess.close()
  print("Indexing finished successfully.")

runner = ArgumentParser()
runner.execute()

if runner.run:
  localization.load_languages()
  server_setup(port=runner.port, cert_file = runner.certificate_file, private_key = runner.private_key)
elif runner.index:
  run_indexer()
elif runner.add_language:
  localization.load_languages()
  if localization.language_exists(runner.language):
    print("A language with this name already exists.")
    sys.exit(1)
  if runner.language.lower() == 'all':
    print("A language with that name cannot be created.")
    sys.exit(1)
  localization.add_new_language(runner.language)
elif runner.update_language:
  localization.load_languages()
  if runner.language == 'all':
    for l in globals.LANGUAGES[1:]:
      localization.update_language(l.name.lower())
  else:
    if not localization.language_exists(runner.language):
      print("A language with this name doesn't exist.")
      sys.exit(1)
    localization.update_language(runner.language)
  print("Finished updating.")
elif runner.compile_language:
  localization.load_languages()
  if runner.language == 'all':
    for l in globals.LANGUAGES[1:]:
      localization.compile_message_catalog(l.name.lower())
  else:
    if not localization.language_exists(runner.language):
      print("A language with this name doesn't exist.")
      sys.exit(1)
    localization.compile_message_catalog(runner.language)
  print("Finished compiling.")
