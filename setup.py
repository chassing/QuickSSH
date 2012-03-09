
import sys
from setuptools import setup, find_packages

from quickssh.main import VERSION

APP = ['quickssh/main.py']
DATA_FILES = ['quickssh/ttk.py']


if sys.platform == 'darwin':
  extra_options = dict(
    app=APP,
    data_files=DATA_FILES,
    options=dict(
      py2app={
      'argv_emulation': False,
      'iconfile': 'quickssh.icns'
    }),
    setup_requires=['py2app'],
  )
else:
  extra_options = dict(
    packages=find_packages(),
    entry_points={
      'console_scripts': [
          'quickssh = quickssh.main:main',
      ]
    },
  )

setup(
  name="QuickSSH",
  version=VERSION,
  description="SSH Quick Starter",
  author='Christian Assing',
  author_email='chris@ca-net.org',
  url='http://github.com/chassing/quickssh/',
  long_description=open('README.md', 'r').read(),
  classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Unix',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Topic :: System :: Systems Administration',
    ],
  **extra_options
)
