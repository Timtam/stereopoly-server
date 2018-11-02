from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Unicode, Integer, func, ForeignKey, Index, collate, Boolean, UniqueConstraint
from sqlalchemy import PrimaryKeyConstraint

Base = declarative_base()

class MoneySchemes(Base):
  __tablename__ = 'money_schemes'
  id = Column(Integer, primary_key=True)
  name = Column(Unicode, index=True, unique=True, nullable=False)
  money1 = Column(Integer)
  money2 = Column(Integer)
  money3 = Column(Integer)
  money4 = Column(Integer)
  money5 = Column(Integer)
  money6 = Column(Integer)
  money7 = Column(Integer)
  money8 = Column(Integer)
  money9 = Column(Integer)
  money10 = Column(Integer)

def setup():
  global Base
  engine = create_engine('sqlite:///stereopoly.db')
  Base.metadata.bind = engine
  Session = sessionmaker(bind=engine)
  Base.metadata.create_all()
  return Session
