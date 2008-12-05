# -*- coding: utf-8 -*-
from sqlalchemy import *

# Conexión a una base de datos
db = create_engine('sqlite:///tutorial.db', echo=False)

############ Definición de tablas ###############

# Definición de un par de tablas
metadata = MetaData()
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('fullname', String(50)),
)

addresses = Table('addresses', metadata, 
  Column('id', Integer, primary_key=True),
  Column('user_id', None, ForeignKey('users.id', ondelete='CASCADE')),
  Column('email_address', String(50), nullable=False)
)

from sqlalchemy.orm import mapper, relation
class User(object):
    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname

    def __repr__(self):
        return "<User('%s','%s')>" % (self.name, self.fullname)

class Address(object):
    def __init__(self, email_address, user_id):
        self.user_id = user_id.id
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s', '%s')>" % (self.email_address,
                self.user_id)


#mapper(User, users)
mapper(Address, addresses)
mapper(User, users, properties=dict(
addresses=relation(Address, backref='users', 
               cascade='all, delete-orphan')
))

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=db, autoflush=True, transactional=True)
session = Session()

