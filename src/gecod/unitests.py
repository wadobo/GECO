# Testing database
def testdb():
    '''
    base de datos
    '''

    import database as db
    database = 'sqlite:///test.sqlite'

    db.create(database)
    s = db.connect(database)
    user = db.User('dani', 'pass')
    password = db.Password('mi pass', 'asfsdaf')
    conffile = db.Conffile('mi file', 'file', '')
    cookie = db.Cookie()

    user.passwords = [password]
    user.conffiles = [conffile]
    user.cookie = cookie
    s.save(user)
    s.commit()

    u = s.query(db.User).first()
    assert u.name == 'dani'
    assert u.password != 'pass'
    assert u.passwords[0].name == 'mi pass'
    assert u.conffiles[0].name == 'mi file'

def testbackend():
    '''
    backend
    '''
    import backend as b

    b.register('dani2', 'pass')
    assert b.check_user_name('dani2')

    c = b.auth('dani2', 'password', password='pass')
    b.set_password(c, 'nuevo', 'xxxx', type='email',
            account='danigm', description="http://mail.danigm.net")
    p = b.get_password(c, 'nuevo')
    assert p.name == 'nuevo'

    b.del_password(c, 'nuevo')
    p = b.get_passwords_by(c, name='nuevo')
    assert not p

    b.unregister(c)
    assert not b.check_user_name('dani2')

if __name__ == '__main__':
    # Se ejecutan todas las funciones que empiezan por test
    for k,v in globals().items():
        if k.startswith('test'):
            print "testing " + v.__doc__
            try:
                v()
                print "...OK"
            except Exception, e:
                print "...BAD", e
