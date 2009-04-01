from distutils.core import setup
import os
import sys
import shutil

datafiles = []

prefix = '/usr'
for arg in sys.argv:
    if arg.startswith('--prefix') or\
            arg.startswith('--home'):
        opt, prefix = arg.split('=')

response = raw_input('Crear base de datos [Y/n]: ')
if not response or response.lower() in ['Yy']:
    from gecod import database
    database.create()
    datafiles.append(('share/gecod/', ['database.sqlite']))

response = raw_input('Generar certificados [Y/n]: ')
if not response or response.lower() in ['Yy']:
    os.chdir('certs')
    os.popen('bash generate-pem.sh')
    os.chdir('..')
    datafiles.append(('share/gecod/certs/', ['certs/cert.pem', 'certs/key.pem']))

conffile = '''host = localhost
port = 4343
database = sqlite://%(path)s/database.sqlite
KEYFILE = %(path)s/certs/key.pem
CERTFILE = %(path)s/certs/cert.pem
''' % {'path': prefix+'/share/gecod'}

conf = open('gecod-xmlrpc.conf', 'w')
conf.write(conffile)
conf.close()

if not os.path.exists('/etc/gecod-xmlrpc.conf'):
    datafiles.append(('/etc/gecod-xmlrpc.conf', ['gecod-xmlrpc.conf']))

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
