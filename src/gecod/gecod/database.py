import sys
from sqlalchemy import *

import sqlalchemy
InvalidRequestError = sqlalchemy.exc.InvalidRequestError
IntegrityError = sqlalchemy.exc.IntegrityError

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relation, backref, sessionmaker

import hashlib
import binascii

import datetime
import random
import string

# 0123456789...ABC....abc
if sys.version_info[0] >= 3:
    letters = string.ascii_letters
else:
    letters = string.letters
CHARS = letters + string.digits + '.:;,!?{}[]<>=-_()+'
DEFAULT_EXPIRATION = 60 # password default expiration (in days)


Base = declarative_base()
metadata = Base.metadata


def password_hash(password, salt=None):
    if not salt:
        from backend import SECRET_KEY as salt
    dk = hashlib.pbkdf2_hmac('sha512', password.encode('utf8'),
                             salt.encode('utf8'), 100000)
    return binascii.hexlify(dk)

def old_password_hash(password):
    from hashlib import sha1
    return sha1(password.encode()).hexdigest()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    password = Column(String(300))

    def set_password(self, password):
        self.password = password_hash(password)

    def check_password(self, password):
        c = (self.password == password_hash(password))

        if c:
            return True

        # rehashing old hashes sha1
        old = old_password_hash(password)
        if old == self.password:
            self.set_password(password)
            return True

        return False

    def __init__(self, name, password):
        self.name = name
        self.set_password(password)

class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    # types = ['generic', 'web', 'email', 'unix']
    type = Column(String(20))
    name = Column(String(50))
    description = Column(String(255))
    updated = Column(DateTime())
    expiration = Column(DateTime())

    account = Column(String(100))
    password = Column(String(1000), nullable=False)
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

    def set_password(self, password, expiration=DEFAULT_EXPIRATION,
            cypher_method=''):
        self.password = password
        self.cypher_method = cypher_method
        default = expiration if expiration else DEFAULT_EXPIRATION
        self.expiration = datetime.datetime.now() +\
            datetime.timedelta(default)

    def serialize(self):
        return dict(type=self.type, name=self.name,
                description=self.description,
                updated=self.updated.strftime("%d/%m/%Y %H:%M:%S"),
                expiration=self.expiration.strftime("%d/%m/%Y %H:%M:%S"),
                account=self.account,
                password=self.password,
                cypher_method=self.cypher_method)

class Conffile(Base):
    __tablename__ = 'conffiles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
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

    # this is a temporal random password used to authenticate after the use
    # of username/password
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

if __name__ == '__main__':
    create()
