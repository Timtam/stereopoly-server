#!/bin/python

from stereopoly.argument_parser import ArgumentParser
from stereopoly.db import setup as db_setup
from stereopoly.indexer import Indexer
from stereopoly.server import setup as server_setup

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

if runner.cmd == 'run':
  server_setup()
elif runner.cmd == 'index':
  run_indexer()
else:
  print('Invalid command.')
  print('Supported commands:')
  print('\tindex - (re)index all news, boards etc.')
  print('\trun - run the server')
