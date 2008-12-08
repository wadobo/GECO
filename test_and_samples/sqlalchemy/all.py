from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation, backref, sessionmaker

Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname

    def __repr__(self):
       return "<User('%s','%s')>" % (self.name, self.fullname)

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relation(User, backref=backref('addresses',
        order_by=id, cascade='all, delete-orphan',
        passive_deletes=False))

    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address

def connect(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    Session = sessionmaker(bind=db, autoflush=True)
    session = Session()
    return session

def create(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    metadata.create_all(db)
