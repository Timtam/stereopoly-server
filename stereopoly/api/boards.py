from stereopoly.db import Board
from stereopoly import globals
from stereopoly.utils import check_app_version, generate_error

@check_app_version
def get_all(api, language):
  session = globals.DB()
  boards = session.query(Board).all()
  session.close()
  return [{'name': _(b.name, language), 'id': b.id, 'version': b.version} for b in boards]

@check_app_version
def get(api, id, language):
  b = None
  session = globals.DB()
  board = session.query(Board).filter_by(id = id).first()
  if not board:
    session.close()
    return generate_error(_("No board found with that id", language)), 400
  b = board.to_dict()
  session.close()
  return b