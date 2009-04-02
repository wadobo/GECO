from distutils.core import setup
import os
import sys
import shutil

datafiles = []

def append(directory):
    base = os.getcwd()
    fulldirectory = os.path.join(base, directory)
    for i in os.listdir(fulldirectory):
        fullpath = os.path.join(fulldirectory, i)
        if os.path.isdir(fullpath):
            append(directory+'/'+i)
        else:
            datafiles.append(('share/web-geco/'+directory, [directory+'/'+i]))

append('templates')
append('static')
append('web')

datafiles.append(('share/web-geco/', ['delete.py',
    'index.py', 'utils.py', 'list.py', 'login.py',
    'new_password.py', 'ajax.py', 'edit.py', 'options.py']))

setup(name = 'web-geco',
      version = '1.0',
      description = 'web client for geco',
      author = 'Daniel Garcia Moreno',
      author_email = '<dani@danigm.net>',
      url = 'http://bzr.danigm.net/geco',
      license = 'GPLv3',
      data_files = datafiles,
      scripts = ['web-geco'],
      packages = ['gecoc']
      )

