import sys
import os
from nose.tools import *
import vs2007
from vs2007 import VS2007Process
from mock import MagicMock
import win32api

from vs2007.control import _parse_options, _start, main

original_metod = None
original = None
saved = None
pid = None

def setup():
	global saved
	saved = sys.argv
	global original
	original = vs2007.VS2007Process
	#win32api.OpenProcess = MagicMock(return_value='process')
	global vs2007p
	vs2007p = vs2007.VS2007Process()
#	vs2007p.process = 'hello process'
#	pid = get_pid()
#	patch_VS2007Process()

def teardown():
#	stop_vs()
	sys.argv = saved
	vs2007.VS2007Process = original

@with_setup(setup, teardown)
def test_version():
	vs2007p.version = '1.120'
	vs2007p.pid = 1100
	assert_equal(vs2007p.version, '1.120')
	assert_equal(vs2007p.pid, 1100)

@with_setup(setup, teardown)
def test_options():
	sys.argv = ['vs2007', '--verbose', 'start']
	args = _parse_options()
	assert_equals(args.verbose, True)
	assert_equals(args.subparser_name, 'start')

def setup_start():
	global original_method
	original_method = VS2007Process.start
	VS2007Process.start = MagicMock(return_value = 1100 )	

def teardown_start():
	VS2007Process.start = original_method

@with_setup(setup_start, teardown_start)
def test_start():
	sys.argv = ['vs2007', '--verbose', 'start']
	main()
	VS2007Process.start.assert_called_once


def setup_stop():
	global original_method
	original_method = VS2007Process.stop
	VS2007Process.stop = MagicMock(return_value = 1100 )	

def teardown_stop():
	VS2007Process.stop = original_method

@with_setup(setup_stop, teardown_stop)
def test_stop():
	sys.argv = ['vs2007', '--verbose', 'stop']
	main()
	VS2007Process.stop.assert_called_once
