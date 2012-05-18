#!/usr/bin/env bash

deactivate || true

rm -rf build dist

# use python2.6 on mac; tkinter focus bug :(
python2.6 setup.py py2app
