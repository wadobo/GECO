from distutils.core import setup
import os
import shutil

datafiles = []

response = raw_input('Crear base de datos [Y/n]: ')
if response.lower() in ['Yy ']:
    import database
    database.create()
    datafiles.append(('gecod/', 'database.sqlite'))

response = raw_input('Generar certificados [Y/n]: ')
if response.lower() in ['Yy ']:
    os.chdir('certs')
    os.popen('bash generate-pem.sh')
    datafiles.append(('gecod/certs/',
        ['certs/cert.pem', 'certs/key.pem']))

if not os.path.exists('/etc/gecod-xmlrpc.conf'):
    shutil.copy('gecod-xmlrpc.conf.example', '/etc/gecod-xmlrpc.conf')

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
