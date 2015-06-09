import sys
import os
import ntpath
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

def setup_mocks():
	vs2007._VS2007Process = vs2007.VS2007Process
	global mock_vs2007p
	mock_vs2007p = MagicMock(return_value = None)
	vs2007.VS2007Process = MagicMock(return_value = mock_vs2007p)

def teardown_mocks():
	vs2007.VS2007Process = vs2007._VS2007Process
	delattr(vs2007, '_VS2007Process')

@with_setup(setup_mocks, teardown_mocks)
def test_open_without_process():
	path = 'C:\\VS2007data\\GrtCCG06'
	sys.argv = ['vs2007', 'open', path]
	vs2007.VS2007Process.is_running = MagicMock(return_value = False)
	main()
	vs2007.VS2007Process.start.assert_called_once_with()
	mock_vs2007p.open_file.assert_called_once_with(path)

@with_setup(setup_mocks, teardown_mocks)
def test_open_with_process():
	path = 'C:\\VS2007data\\GrtCCG06'
	sys.argv = ['vs2007', 'open', path]
	vs2007.VS2007Process.is_running = MagicMock(return_value = True)
	main()
	#vs2007.VS2007Process.start.assert_called_once_with()
	mock_vs2007p.open_file.assert_called_once_with(path)


@with_setup(setup_mocks, teardown_mocks)
def test_stop():
	sys.argv = ['vs2007', '--verbose', 'stop']
	main()
	vs2007.VS2007Process.stop.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_start():
	sys.argv = ['vs2007', '--verbose', 'start']
	main()
	vs2007.VS2007Process.start.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_pwd():
	sys.argv = ['vs2007', '--verbose', 'pwd']
	main()
	mock_vs2007p.pwd.assert_called_once_with()
