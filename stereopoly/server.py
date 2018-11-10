from flask import render_template
import connexion
from OpenSSL import SSL

from stereopoly.config import Config
from stereopoly import db
from stereopoly import globals
from stereopoly.path import get_script_directory

import os
import os.path

def setup(port, cert_file=None, private_key=None):
  app = connexion.App(__name__, specification_dir = './')
  app.app.config.from_object(Config)
  app.add_api(os.path.join(get_script_directory(), 'var', 'stereopoly.yml'), validate_responses=True)

  globals.APP = app
  globals.DB = db.setup()

  @app.route('/')
  def home():
    return render_template('home.html')

  context = None
  if cert_file and private_key:
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_private_key_file(private_key)
    context.use_certificate_file(cert_file)

  app.run(port=port, debug = True, ssl_context = context)
