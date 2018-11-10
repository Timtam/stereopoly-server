import argparse
import sys

class ArgumentParser(object):
  def __init__(self):
    self.parser=argparse.ArgumentParser()
    self.parser.add_argument("cmd", help="Command to run")
    self.parser.add_argument("-p", "--port", help="port to listen on", type=int, default=5000)

  def execute(self):
    args=self.parser.parse_args()

    self.cmd = args.cmd
    self.port = args.port
