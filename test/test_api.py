import sys
import os
from nose.tools import *
from vs2007.api import *

saved = None

def setup():
	global saved
	saved = sys.argv

def teardown():
	sys.argv = saved

