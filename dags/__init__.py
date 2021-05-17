"""
This module enables this package to access modules from an upper directory.
"""
import os.path
import sys

def set_script_path():
    PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    sys.path = [PROJECT_DIR] + sys.path

set_script_path()
