from flask import render_template
import connexion

from stereopoly.config import Config
from stereopoly.db import setup as db_setup
from stereopoly import globals

import os

app = connexion.App(__name__, specification_dir = './')
app.app.config.from_object(Config)
app.add_api("stereopoly.yml")

globals.DB = db_setup()

@app.route('/')
def home():
  return render_template('home.html')
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug = True)
