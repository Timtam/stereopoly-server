import argparse
import sys

class ArgumentParser(object):
  def __init__(self):
    self.parser=argparse.ArgumentParser()
    self.parser.add_argument("cmd", help="Command to run")
    self.parser.add_argument("-c", "--certificate-file", help="certificate pem file", type=str, default=None)
    self.parser.add_argument("-p", "--port", help="port to listen on", type=int, default=5000)
    self.parser.add_argument("-r", "--private-key", help="private key pem file", type=str, default=None)

  def execute(self):
    args=self.parser.parse_args()

    self.cmd = args.cmd
    self.cert_file = args.certificate_file
    self.port = args.port
    self.private_key = args.private_key
