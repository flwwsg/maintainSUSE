#!/usr/bin/python3
"""
inital file for bash
"""

from commonInit import *

changeMod()
fpath = os.path.abspath(__file__)
file = fpath.replace('init', 'init_'+USER)
exec(compile(open(file).read(), file, 'exec'))