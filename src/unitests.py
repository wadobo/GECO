# Testing database
def testdb():
    import database as db

    db.create()
    s = db.connect()
    user = db.User('dani', 'pass')
    password = db.Password('mi pass', 'asfsdaf')
    conffile = db.Conffile('mi file', 'file', '')

    user.passwords = [password]
    user.conffiles = [conffile]
    s.save(user)
    s.commit()

    u = s.query(db.User).first()
    assert u.name == 'dani'
    assert u.password != 'pass'
    assert u.passwords[0].name == 'mi pass'
    assert u.conffiles[0].name == 'mi file'
