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
  Column('user_id', None, ForeignKey('users.id')),
  Column('email_address', String(50), nullable=False)
)

#################################################

# Esto crea las tablas en la base de datos
metadata.create_all(db)

################### Uso básico ##################
# Para insertar datos en una tabla
ins = users.insert(values={'name':'jack', 'fullname':'Jack Jones'})
#str(ins)

# Para ejecutar algo se hace con execute
result = db.execute(ins)
print result.last_inserted_ids()

# Otra forma de ejecutar insert
ins = users.insert()
db.execute(ins, name='wendy', fullname='Wendy Williams')
db.execute(addresses.insert(), [ 
   {'user_id': 1, 'email_address' : 'jack@yahoo.com'},
   {'user_id': 1, 'email_address' : 'jack@msn.com'},
   {'user_id': 2, 'email_address' : 'www@www.org'},
   {'user_id': 2, 'email_address' : 'wendy@aol.com'},
])

# Una forma de hacer consultas
s = select([users], users.c.name == 'jack')
result = db.execute(s)
print list(result)
# Otra forma de hacer consultas
s = users.select()
s = s.where(users.c.name=='jack')
print list(result)
#################################################

print "ORM"
############## ORM #############

# http://www.sqlalchemy.org/docs/04/ormtutorial.html

# Después de definir la tabla se puede asociar a una clase
from sqlalchemy.orm import mapper
class User(object):
    def __init__(self, name, fullname):
        self.name = name
        self.fullname = fullname

    def __repr__(self):
        return "<User('%s','%s')>" % (self.name, self.fullname)

class Address(object):
    def __init__(self, email_address):
        self.email_address = email_address

    def __repr__(self):
        return "<Address('%s')>" % self.email_address


mapper(User, users)
mapper(Address, addresses)
#mapper(User, users_table, properties={    
#    'addresses':relation(Address, backref='user')
#    })

ed_user = User('ed', 'Ed Jones')

# Pero para guardar los cambios en la base de datos hay que crear una
# sesión
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=db, autoflush=True, transactional=True)
session = Session()
# Y con esto se aplica en la base de datos
session.save(ed_user)

# Y se pueden hacer consultas
print session.query(User).filter_by(name='ed').all()
# También por id
print session.query(User).get(1)
# Y se pueden concatenar
print session.query(User).filter(User.id<2).filter_by(name='ed').\
     filter(User.fullname=='Ed Jones').all()
# Y hacer joins
print "join ", session.query(User).add_entity(Address).\
    filter(Address.email_address=='jack@yahoo.com').filter(Address.user_id == User.id).all()

# Y modificar
session.query(User).filter_by(name='ed').first().fullname = "Noooor"
print list(session.query(User).filter_by(name='ed'))
session.commit()

# Y borrar
session.delete(ed_user)


# cerrando todo
from sqlalchemy.orm import clear_mappers
session.close()
clear_mappers()


################################
