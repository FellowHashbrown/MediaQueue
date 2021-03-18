"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['MediaQueue.py']
DATA_FILES = []
OPTIONS = {'iconfile': 'mediaqueue.icns', 'plist': 'Info.plist'}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
