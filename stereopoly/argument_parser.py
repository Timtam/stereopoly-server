import argparse
import sys

class ArgumentParser(object):
  def __init__(self):
    self.parser=argparse.ArgumentParser()
    self.parser.add_argument("cmd", help="Command to run")

  def execute(self):
    args=self.parser.parse_args()

    self.cmd = args.cmd
