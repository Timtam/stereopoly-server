from stereopoly.db import Board
from stereopoly import globals
from stereopoly.utils import check_app_version, generate_error

@check_app_version
def get_all(api):
  session = globals.DB()
  boards = session.query(Board).all()
  session.close()
  return [{'name': b.name, 'id': b.id, 'version': b.version} for b in boards]

@check_app_version
def get(api, id):
  session = globals.DB()
  board = session.query(Board).filter_by(id = id).first()
  if not board:
    session.close()
    return generate_error("No board found with that id"), 400
  return board.to_dict()