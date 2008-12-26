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
