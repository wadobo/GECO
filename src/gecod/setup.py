from distutils.core import setup
import os
import sys

datafiles = []

ask = lambda x: 'N'
prefix = '/usr'

for arg in sys.argv:
    if arg.startswith('--prefix') or\
            arg.startswith('--home'):
        opt, prefix = arg.split('=')
    elif arg.startswith('--ask'):
        ask = raw_input

#response = ask('Crear base de datos [Y/n]: ')
#if not response or response.lower() in 'Yy':
#    from gecod import database
#    database.create()
#    datafiles.append(('share/gecod/', ['database.sqlite']))
#
#response = ask('Generar certificados [Y/n]: ')
#if not response or response.lower() in 'Yy':
#    os.chdir('certs')
#    os.popen('bash generate-pem.sh')
#    os.chdir('..')
#    datafiles.append(('share/gecod/certs/', ['certs/cert.pem', 'certs/key.pem']))

conffile = '''host = localhost
port = 4343
database = sqlite:///%(path)s/database.sqlite
KEYFILE = %(path)s/certs/key.pem
CERTFILE = %(path)s/certs/cert.pem
''' % {'path': prefix+'/share/gecod'}

conf = open('gecod-xmlrpc.conf', 'w')
conf.write(conffile)
conf.close()

if not os.path.exists(prefix+'/../etc/gecod-xmlrpc.conf'):
    datafiles.append((prefix+'/../etc', ['gecod-xmlrpc.conf']))

setup(name = 'gecod-xmlrpc',
      version = '1.0',
      description = 'gecod xmlrpc server',
      author = 'Daniel Garcia Moreno',
      author_email = '<dani@danigm.net>',
      url = 'http://bzr.danigm.net/geco',
      license = 'GPLv3',
      data_files = datafiles,
      scripts = ['gecod-xmlrpc'],
      packages = ['gecod']
      )

