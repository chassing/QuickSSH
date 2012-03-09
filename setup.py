
from setuptools import setup

APP = ['quickssh/main.py']
DATA_FILES = ['quickssh/ttk.py']
OPTIONS = {
  'argv_emulation': False,
  'iconfile': 'quickssh.icns'
}

setup(
    app=APP,
    name="QuickSSH",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
