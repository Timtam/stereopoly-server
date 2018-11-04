from stereopoly.db import Board
from stereopoly import globals
from stereopoly.utils import check_app_version

@check_app_version
def get(api):
  session = globals.DB()
  boards = session.query(Board).all()
  session.close()
  return [{'name': b.name, 'id': b.id, 'version': b.version} for b in boards]
