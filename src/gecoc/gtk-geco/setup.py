from distutils.core import setup
import os

datafiles = []

for i in os.listdir('glade'):
    datafiles.append(('share/gtk-geco/', ['glade/'+i]))

datafiles.append(('share/pixmaps', ['geco.png']))
datafiles.append(('share/applications', ['gtkgeco.desktop']))

setup(name = 'gtk-geco',
      version = '1.0',
      description = 'gtk client for geco',
      author = 'Daniel Garcia Moreno',
      author_email = '<dani@danigm.net>',
      url = 'http://bzr.danigm.net/geco',
      license = 'GPLv3',
      data_files = datafiles,
      scripts = ['gtk-geco', 'gecosearch'],
      packages = ['keyring', 'keyring.tests', 'keyring.util',
                  'keyring.backends'],
      py_modules = ['gtkgeco'],
      )

