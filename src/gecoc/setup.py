from distutils.core import setup
import os
import sys
import shutil

setup(name = 'gecoc',
      version = '1.0',
      description = 'geco client lib',
      author = 'Daniel Garcia Moreno',
      author_email = '<dani@danigm.net>',
      url = 'http://bzr.danigm.net/geco',
      license = 'GPLv3',
      scripts = ['terminal-geco'],
      packages = ['gecoc']
      )

