# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relation

########### Metaclase ##########################

class SQLtable(type):
    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        properties = dict()
        if cls.__dict__.has_key('relations'):
            for table in cls.relations:
                table_name = table.table.name
                property = relation(table, backref=cls.table.name,
                        cascade='all, delete-orphan')
                properties[table_name] = property

        mapper(cls, cls.table, properties)

############ Definición de tablas ###############

from sqlalchemy.orm import mapper, relation
metadata = MetaData()

class Address:
    __metaclass__ = SQLtable

    table = Table('addresses', metadata, 
      Column('id', Integer, primary_key=True),
      Column('user_id', None, ForeignKey('users.id', ondelete='CASCADE')),
      Column('email_address', String(50), nullable=False)
    )

    def __init__(self, email_address, user_id):
        self.user_id = user_id.id
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s', '%s')>" % (self.email_address,
                self.user_id)

class User:
    __metaclass__ = SQLtable

    table = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('fullname', String(50)),
    )
    relations = [Address,]

    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname

    def __repr__(self):
        return "<User('%s','%s')>" % (self.name, self.fullname)

# Conexión a una base de datos
def connect(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    Session = sessionmaker(bind=db, autoflush=True, transactional=True)
    session = Session()
    return session

def create(database='sqlite:///database.sqlite'):
    db = create_engine(database, echo=False)
    metadata.create_all(db)
