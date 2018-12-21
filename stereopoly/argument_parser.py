import argparse
import sys

class ArgumentParser(object):

  add_language = False
  certificate_file = None
  index = False
  language = ''
  port = 5000
  private_key = None
  run = False
  update_language = False

  def __init__(self):
    self.parser=argparse.ArgumentParser()
    global_subparsers = self.parser.add_subparsers(
      title = 'sub-commands',
      description = 'valid sub-commands',
      dest = 'subparser_name',
      help = 'perform the various actions for the stereopoly server'
    )
    index_parser = global_subparsers.add_parser('index', help='(re)index the yaml files into the database')
    language_parser = global_subparsers.add_parser('language',
      help = 'perform various localization-related tasks'
    )
    language_subparsers = language_parser.add_subparsers(
      title = 'sub-commands',
      description = 'valid sub-commands',
      dest = 'language_subparser_name',
      help = 'add and edit translations'
    )
    language_add_parser = language_subparsers.add_parser('add',
      help='add a new language'
    )
    language_add_parser.add_argument('lang',
      type=str,
      help='name of the language which will be added'
    )
    language_update_parser = language_subparsers.add_parser('update',
      help='update po catalog for specific language'
    )
    language_update_parser.add_argument('lang',
      type=str,
      help='name of the language which will be updated (all to update all languages)'
    )
    run_parser = global_subparsers.add_parser('run', help='run this server')
    run_parser.add_argument("-c", "--certificate-file", help="certificate pem file", type=str, default=None)
    run_parser.add_argument("-p", "--port", help="port to listen on", type=int, default=5000)
    run_parser.add_argument("-r", "--private-key", help="private key pem file", type=str, default=None)

  def execute(self):
    args=self.parser.parse_args()

    if args.subparser_name == 'index':
      self.index = True
    elif args.subparser_name == 'run':
      self.port = args.port
      self.certificate_file = self.certificate_file
      self.private_key = self.private_key
      self.run = True
    elif args.subparser_name == 'language':
      if args.language_subparser_name == 'add':
        self.add_language = True
        self.language = args.lang.lower()
      elif args.language_subparser_name == 'update':
        self.update_language = True
        self.language = args.lang.lower()
      else:
        self.parser.parse_args(['language', '--help'])
    else:
      args = self.parser.parse_args(['--help'])
