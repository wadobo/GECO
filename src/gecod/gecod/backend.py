'''
Provides somes functions to interact with database withouth knowing
it. Gecod-backend provides an abstraction layer over gecod-database.
'''

import sys
import database as db
import datetime
import time
from functools import wraps

DATABASE = 'sqlite:///database.sqlite'
SECRET_KEY = 'v!r#8-@l!0e__nior8(nwst!s&s$51+qu+^^(04q3w!nd1v_u9'

class NotImplementedError(Exception):
    pass

class ImportError(Exception):
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
    @wraps(function)
    def new_funct(*args, **kwargs):
        s = kwargs.get('session', '')
        if not s:
            session = db.connect(DATABASE)
            try:
                kwargs['session'] = session
                result = function(*args, **kwargs)
            finally:
                session.close()
        else:
            result = function(*args, **kwargs)

        return result

    new_funct.__doc__ = function.__doc__
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

    def __str__(self):
        n = self.name
        t = self.type
        d = self.description
        a = self.account
        p = self.password
        c = self.cypher_method
        u = self.updated
        e = self.expiration

        def fix_encoding(cad):
            try:
                return str(cad)
            except:
                return cad.encode("utf-8")

        return "|".join(map(fix_encoding, (n,t,d,a,p,c,u,e)))


def user_by_cookie(cookie, session=None):
    '''
    Return the user with that cookie. If cookie is expired or not
    found raises BadCookieError

    session is a database.connect() object
    '''

    close_it = False
    if not session:
        session = db.connect(DATABASE)

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
def auth_by_password(name, password, session=None):
    '''
    def auth_by_password(name, password, session=None):

    Authenticate an user by name and password.
    If user exists and password is correct, return a cookie
    In other case return None
    '''

    try:
        db_user = session.query(db.User).\
                filter(db.User.name == name).one()
    except db.InvalidRequestError:
        return None

    if not db_user.check_password(password):
        return None

    # Return the current cookie if it's valid yet
    if db_user.cookie and\
            db_user.cookie.expiration > datetime.datetime.now():
        return db_user.cookie.id

    cookie = db.Cookie()
    db_user.cookie = cookie
    session.commit()
    return cookie.id

@session_decorator
def logout(cookie, session=None):
    '''
    def logout(cookie, session=None):

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
def get_all_passwords(cookie, session=None, from_db=False):
    '''
    def get_all_passwords(cookie, session=None, from_db=False):

    Returns a generator (iterable) of passwords with all passwords
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

def export(cookie):
    '''
    Returns a string with all passwords
    '''

    return "\n".join([str(p).replace('\n', '\\n')\
            for p in get_all_passwords(cookie)])

@session_decorator
def restore(cookie, data, session=None):
    '''
    def restore(cookie, data, session=None):

    data must be a string generated by export
    name|type|description|account|password|cypher_method|updated|expiration

    if a password exists and it's older, it's replaced
    '''
    user = user_by_cookie(cookie, session)

    passwords = data.split('\n')
    for p in passwords:
        try:
            name, type, description, account, password, cypher_method, updated, expiration = p.split("|")
            expiration = datetime.datetime.fromtimestamp(float(expiration))
            updated = datetime.datetime.fromtimestamp(float(updated))
            name, type, description, account =\
                    map(lambda x: x.replace("\\n", "\n"), (name, type, description, account))

            kwargs = dict(type=type, description=description,
                    account=account, cypher_method=cypher_method)

            exists = False
            oldp = None
            for ep in user.passwords:
                if ep.name == name:
                    exists = True
                    oldp = ep
                    break

            if exists:
                if updated > oldp.updated:
                    session.delete(oldp)
                else:
                    continue

            new_password = db.Password(name, password, **kwargs)
            new_password.updated = updated
            new_password.expiration = expiration

            user.passwords.append(new_password)
            session.commit()

        except Exception as e:
            raise ImportError("can't import '%s': %s" % (p, e.message))

@session_decorator
def get_passwords_by(cookie, session=None, from_db=False, **kwargs):
    '''
    def get_passwords_by(cookie, session=None, from_db=False, **kwargs):

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
def set_password(cookie, name, password, session=None, **kwargs):
    '''
    def set_password(cookie, name, password, session=None, **kwargs):

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
def del_password(cookie, name, session=None):
    '''
    def del_password(cookie, name, session=None):

    Delete a password by name
    '''

    try:
        password = get_passwords_by(cookie, name=name,
                session=session, from_db=True).first()
    except db.InvalidRequestError:
        raise NotFoundError("Can't found password by name %s" % name)
    session.delete(password)
    session.commit()

@session_decorator
def register(name, password, session=None):
    '''
    def register(name, password, session=None):

    Register a new user in GECO

    Can raise RegisteredUserError
    '''

    try:
        new_user = db.User(name, password)
        session.add(new_user)
        session.commit()
    except db.IntegrityError:
        raise RegisteredUserError('User %s is registered' % name)

@session_decorator
def check_user_name(name, session=None):
    '''
    def check_user_name(name, session=None):

    Return True if name is a username registered
    '''

    names = session.query(db.User).\
            filter(db.User.name == name).first()

    return bool(names)

@session_decorator
def unregister(cookie, session=None):
    '''
    def unregister(cookie, session=None):

    deletes a user
    '''

    user = user_by_cookie(cookie, session)
    session.delete(user)
    session.commit()

@session_decorator
def change_password(cookie, new_password, session=None):
    '''
    def change_password(cookie, new_password, session=None):

    Changes the user password
    '''

    user = user_by_cookie(cookie, session)
    user.set_password(new_password)
    session.commit()

@session_decorator
def change_attr(cookie, name, session=None, **kwargs):
    '''
    def change_attr(cookie, name, **kwargs):

    Changes all attrs of the password named name.
    example:
        change_attr('asdfsadf', 'mypassword', password='asdfasdfxcv',
                account='newaccount')
    '''

    user = user_by_cookie(cookie, session)
    try:
        password = session.query(db.Password)\
                .filter(db.Password.user_id == user.id)

        password = password.filter_by(name=name).first()

    except db.InvalidRequestError:
        raise NotFoundError("Can't found password by name %s" % name)

    for key, value in kwargs.items():
        setattr(password, key, value)

    session.commit()
