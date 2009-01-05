# -*- coding: utf-8 -*-

# En principio pensaba hacerlo con sqlojbect, pero voy a
# hacerlo con sqlalchemy que parece que es más potente y así aprendo
# una cosa nueva.

# De momento necesito las siguientes tablas:
#  - usuario: (nombre, contraseña, email)
#  - contraseña: (identificador, recurso, cadena, usuario, fecha de creación,
#                   fecha de caducidad)

import sys
from sqlalchemy import *
from sqlalchemy.exceptions import InvalidRequestError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation, backref, sessionmaker

# python 2.6 compatible
if sys.version_info[1] == 6:
    from hashlib import sha1 as sha
else:
    import sha
    sha = sha.new

import datetime
import random
import string

# 0123456789...ABC....abc
CHARS = string.letters + string.digits + '.:;,!?{}[]<>=-_()+'
DEFAULT_EXPIRATION = 60 # password default expiration (in days)


Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    password = Column(String(60))

    def __init__(self, name, password):
        self.name = name
        self.password = sha(password).hexdigest()

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    # types = ['generic', 'web', 'email', 'unix']
    type = Column(String(20))
    name = Column(String(20))
    description = Column(String(255))
    updated = Column(DateTime())
    expiration = Column(DateTime())

    account = Column(String(100))
    password = Column(String(100), nullable=False)
    cypher_method = Column(String(20))

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relation(User, backref=backref('passwords',
        order_by=id, cascade='all, delete-orphan',
        passive_deletes=False))

    def __init__(self, name, password, type='generic',
            description='', account='', expiration=DEFAULT_EXPIRATION,
            cypher_method=''):
        self.name = name
        self.password = password
        self.type = type
        self.description = description
        self.account = account
        self.cypher_method = cypher_method
        self.updated = datetime.datetime.now()
        default = expiration if expiration else DEFAULT_EXPIRATION

        self.expiration = datetime.datetime.now() +\
            datetime.timedelta(default)

class Conffile(Base):
    __tablename__ = 'conffiles'

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    description = Column(String(255))
    updated = Column(DateTime())

    # relpath start at $HOME
    rel_path = Column(String(500), nullable=False)
    filename = Column(String(500), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relation(User, backref=backref('conffiles',
        order_by=id, cascade='all, delete-orphan',
        passive_deletes=False))

    def __init__(self, name, filename, relpath, description=''):
        self.name = name
        self.filename = filename
        self.rel_path = relpath
        self.description = description
        self.updated = datetime.datetime.now()

class Cookie(Base):
    __tablename__ = 'cookies'

    # El id es una especie de cookie que se va a envia desde el
    # frontend al backend de gecod, nunca al cliente. Es una forma de
    # no guardar la contraseña, ni siquiera el hash de esta
    id = Column(String(80), primary_key=True)
    expiration = Column(DateTime())
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relation(User, backref=backref('cookie',
        uselist=False,
        order_by=id, cascade='all, delete-orphan',
        passive_deletes=False))

    def __init__(self):
        # Un dia de expiración de cookie es mucho?
        self.id = ''.join([random.choice(CHARS) for _ in range(80)])
        self.expiration = datetime.datetime.now() +\
            datetime.timedelta(1)

def connect(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    Session = sessionmaker(bind=db, autoflush=True)
    session = Session()
    return session

def create(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    metadata.create_all(db)
