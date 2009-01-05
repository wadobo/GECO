# -*- coding: utf-8 -*-

'''
Provides somes functions to interact with database withouth knowing
it. Gecod-backend provides an abstraction layer over gecod-database.
'''

# ============================================================ #
# TODO Funciones necesarias:                                   #
#                                                              #
# - Diferentes metodos de autenticación                        # 
# - consultar ficheros de configuración                        # 
# - almacenar ficheros de configuración                        #
# - borrado de ficheros de configuración                       #
#                                                              # 
# ============================================================ #

import sys
import database as db
import datetime
import time

class NotImplementedError(Exception):
    pass

class BadCookieError(Exception):
    pass

class NotFoundError(Exception):
    pass

class RegisteredUserError(Exception):
    pass

def session_decorator(function):
    '''
    decorator that set the session variable to use inside a function.
    With that decorator it's possible to use the session variable like
    if a global variable session is declared.

    session is a sqlalchemy session, and you can get one calling
    database.connect() or backend.db.connect()
    '''
    def new_funct(*args, **kwargs):
        session = db.connect()
        function.__globals__['session'] = session
        try:
            result = function(*args, **kwargs)
        finally:
            session.close()
        return result

    return new_funct

def generator_filtered(filter, seed):
    for s in seed:
        yield filter(s)

class Password:
    def __init__(self, password):
        self.type = password.type
        self.name = password.name
        self.description = password.description
        self.account = password.account
        self.password = password.password
        self.cypher_method = password.cypher_method

        self.updated = time.mktime(password.updated.timetuple())
        self.expiration = time.mktime(password.expiration.timetuple())

def user_by_cookie(cookie, session=None):
    '''
    Return the user with that cookie. If cookie is expired or not
    found raises BadCookieError

    session is a database.connect() object
    '''

    close_it = False
    if not session:
        session = db.connect()
    
    try:
        user = session.query(db.User).\
                filter(db.User.id == db.Cookie.user_id).\
                filter(db.Cookie.id == cookie).one()
        expiration = user.cookie.expiration
    except db.InvalidRequestError:
        raise BadCookieError("cookie can't be found")

    # Comprobar que la cookie no está caducada
    if expiration < datetime.datetime.now():
        raise BadCookieError("cookie has expired")
    else:
        return user

def auth(name, method, **kwargs):
    '''
    Authenticate an user and return a cookie to call others functions.
    name is the name of the user
    method is the authentication method (a string)
    
    implemented methods:
        password: for example auth('myname', 'password', password='mypassword')
        ...

    If auth fails it's return None
    If method isn't implemented a NotImplementedError exceptions is raised
    '''

    if method == 'password':
        return auth_by_password(name, kwargs['password'])
    else:
        raise NotImplementedError('Authentication method %s not implemented' %\
                method)

@session_decorator
def auth_by_password(name, password):
    '''
    Authenticate an user by name and password.
    If user exists and password is correct, return a cookie
    In other case return None
    '''

    # python 2.6 compatible
    if sys.version_info[1] == 6:
        from hashlib import sha1 as sha
    else:
        import sha
        sha = sha.new

    password_hash = sha(password).hexdigest()
    try:
        db_user = session.query(db.User).\
                filter(db.User.name == name).one()
    except db.InvalidRequestError:
        return None

    if db_user.password == password_hash:
        # si el usuario ya tiene una cookie, devolver esta
        cookie = db.Cookie()
        db_user.cookie = cookie
        session.commit()
        return cookie.id
    else:
        return None

@session_decorator
def logout(cookie):
    '''
    Deletes the cookie from database. 
    '''
    try:
        c = session.query(db.Cookie).filter(db.Cookie.id == cookie).one()
        session.delete(c)
        session.commit()
    except db.InvalidRequestError:
        pass

def get_password(cookie, name='', from_db=False):
    '''
    Return the password by name of user designed by cookie.

    If from_db is True return a sqlalchemy object

    Can Raise BadCookieError, NotFoundError
    '''
    try:
        password = get_passwords_by(cookie, name=name, from_db=True).first()
    except db.InvalidRequestError:
        raise NotFoundError("Can't found password by name %s" % name)

    if not password:
        raise NotFoundError("Can't found password by name %s" % name)

    if from_db:
        return password
    else:
        return Password(password)

@session_decorator
def get_all_passwords(cookie, from_db=False):
    '''
    Return a generator (iterable) of passwords with all passwords
    '''
    user = user_by_cookie(cookie, session)
    try:
        password = session.query(db.Password)\
                .filter(db.Password.user_id == user.id)

        password = password.all()

    except db.InvalidRequestError:
        raise NotFoundError("Some error has happened")

    if from_db:
        return password
    else:
        return generator_filtered(Password, password)

@session_decorator
def get_passwords_by(cookie, from_db=False, **kwargs):
    '''
    Return a generator (iterable) of passwords by attributes of user
    by cookie.

    If from_db is True return a sqlalchemy object

    permited attributes:
    name, type, updated, expiration, account

    example: get_passwords_by(cookie, name="google", type="mail")

    Can Raise BadCookieError, NotFoundError
    '''
    # argumentos permitidos:
    # name, type, updated, expiration, account,
    permited = ('name', 'type', 'updated', 'expiration', 'account')
    for key in kwargs:
        if key not in permited:
            raise NameError("name '%s' is not defined" % key)

    user = user_by_cookie(cookie, session)
    try:
        password = session.query(db.Password)\
                .filter(db.Password.user_id == user.id)

        password = password.filter_by(**kwargs)

    except db.InvalidRequestError:
        raise NotFoundError("Can't found password by name %s" % name)

    if from_db:
        return password
    else:
        return generator_filtered(Password, password)

@session_decorator
def set_password(cookie, name, password, **kwargs):
    '''
    Add a password to an user by cookie

    name is the name of the password, and password the crypted
    password (Don't pass clear password to this function, it not
    crypt)

    Can also specify:
        - type: generic, web, email, unix
        - description: a sort description 255 chars
        - account: the username o account associated (web, email or unix)
        - expiration: password warning expiration, a datetime in the
              future
    '''

    user = user_by_cookie(cookie, session)
    new_password = db.Password(name, password, **kwargs)
    user.passwords.append(new_password)
    session.commit()

@session_decorator
def del_password(cookie, name):
    '''
    Delete a password by name
    '''

    password = get_password(cookie, name=name, from_db=True)
    session.delete(password)
    session.commit()

@session_decorator
def register(name, password):
    '''
    Register a new user in GECO
    
    Can raise RegisteredUserError
    '''

    try:
        new_user = db.User(name, password)
        session.save(new_user)
        session.commit()
    except db.IntegrityError:
        raise RegisteredUserError('User %s is registered' % name)

@session_decorator
def check_user_name(name):
    '''
    Return True if name is a username registered
    '''

    names = session.query(db.User).\
            filter(db.User.name == name).first()

    return bool(names)

@session_decorator
def unregister(cookie):
    '''
    deletes a user
    '''

    user = user_by_cookie(cookie, session)
    session.delete(user)
    session.commit()
