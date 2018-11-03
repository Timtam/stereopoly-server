from stereopoly.db import Board
from stereopoly import globals

def get():
  session = globals.DB()
  boards = session.query(Board).all()
  return [{'name': b.name, 'id': b.id, 'version': b.version} for b in boards]
