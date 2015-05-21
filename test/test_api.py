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

@with_setup(setup, teardown)
def test_exe_path():
	sys.argv = ['vs2007-api', 'TEST_CMD']
	main()
