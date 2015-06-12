import sys
import os
import ntpath
from nose.tools import *
import vs2007
from vs2007.process import VS2007Process
from mock import MagicMock
import win32api

from vs2007.command_control import _parse_options, _start, _output, main

original_metod = None
original = None
saved = None
pid = None

def setup():
 	global saved
 	saved = sys.argv
	global original
	original = vs2007.process.VS2007Process
	#win32api.OpenProcess = MagicMock(return_value='process')
	global vs2007p
	vs2007p = vs2007.process.VS2007Process()
#	vs2007p.process = 'hello process'
#	pid = get_pid()
#	patch_VS2007Process()

def teardown():
# #	stop_vs()
 	sys.argv = saved
	vs2007.process.VS2007Process = original

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
	vs2007._VS2007Process = vs2007.process.VS2007Process
	global mock_vs2007p
	mock_vs2007p = MagicMock(return_value = None)
	vs2007.process.VS2007Process = MagicMock(return_value = mock_vs2007p)

def teardown_mocks():
	vs2007.process.VS2007Process = vs2007._VS2007Process
	delattr(vs2007, '_VS2007Process')

def test_help():
	sys.argv = ['vs', '--help']
	assert_raises(SystemExit, _parse_options)

@with_setup(setup_mocks, teardown_mocks)
def test_info():
	sys.argv = ['vs', 'info']
	vs2007.command_control._output = MagicMock(return_value = None)
	mock_vs2007p._get_version = MagicMock(return_value = '1.120')
	main()
	vs2007.command_control._output.assert_called_once_with('vs %s with VisualStage 1.120' % vs2007._version.__version__)
	#assert_raises(SystemExit, _parse_options)

@with_setup(setup_mocks, teardown_mocks)
def test_open_without_process():
	path = 'C:\\VS2007data\\GrtCCG06'
	sys.argv = ['vs2007', 'open', path]
	vs2007.process.VS2007Process.is_running = MagicMock(return_value = False)
	main()
	vs2007.process.VS2007Process.start.assert_called_once_with()
	mock_vs2007p.file_open.assert_called_once_with(path)

@with_setup(setup_mocks, teardown_mocks)
def test_open_with_process():
	path = 'C:\\VS2007data\\GrtCCG06'
	sys.argv = ['vs2007', 'open', path]
	vs2007.process.VS2007Process.is_running = MagicMock(return_value = True)
	main()
	#vs2007.process.VS2007Process.start.assert_called_once_with()
	mock_vs2007p.file_open.assert_called_once_with(path)


@with_setup(setup_mocks, teardown_mocks)
def test_stop():
	sys.argv = ['vs2007', '--verbose', 'stop']
	main()
	vs2007.process.VS2007Process.stop.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_start():
	sys.argv = ['vs2007', '--verbose', 'start']
	main()
	vs2007.process.VS2007Process.start.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_status_with_pid():
	sys.argv = ['vs2007', 'status']
	vs2007.process.VS2007Process.get_pid = MagicMock(return_value = 160012)
	vs2007.command_control._output = MagicMock(return_value = None)
	main()
	vs2007.process.VS2007Process.get_pid.assert_called_once_with()
	vs2007.command_control._output.assert_called_once_with('RUNNING 160012')

@with_setup(setup_mocks, teardown_mocks)
def test_status_without_pid():
	sys.argv = ['vs2007', 'status']
	vs2007.process.VS2007Process.get_pid = MagicMock(return_value = None)
	vs2007.command_control._output = MagicMock(return_value = None)
	main()
	vs2007.process.VS2007Process.get_pid.assert_called_once_with()
	vs2007.command_control._output.assert_called_once_with('STOPPED')

@with_setup(setup_mocks, teardown_mocks)
def test_pwd():
	sys.argv = ['vs2007', '--verbose', 'pwd']
	main()
	mock_vs2007p.pwd.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_close():
	sys.argv = ['vs2007', 'close']
	main()
	mock_vs2007p.file_close.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_save():
	sys.argv = ['vs2007', 'save']
	main()
	mock_vs2007p.file_save.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_list_help():
	sys.argv = ['vs', 'list', '-h']
	assert_raises(SystemExit, _parse_options)
	#mock_vs2007p.list_address.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_list_address():
	sys.argv = ['vs', 'list', 'address']
	mock_address = MagicMock(return_value = None)
	mock_vs2007p.get_address_list = MagicMock(return_value = [mock_address])
	main()
	mock_vs2007p.get_address_list.assert_called_once_with(None)
	mock_address.to_s.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_list_address_with_index():
	sys.argv = ['vs', 'list', 'address', '453']
	main()
	mock_vs2007p.get_address_list.assert_called_once_with(453)

@with_setup(setup_mocks, teardown_mocks)
def test_list_attach():
	sys.argv = ['vs', 'list', 'attach']
	mock_address = MagicMock(return_value = None)
	mock_attach = MagicMock(return_value = None)
	mock_address.get_attachlist = MagicMock(return_value = [mock_attach])
	mock_vs2007p.get_address_list = MagicMock(return_value = [mock_address])
	main()
	mock_vs2007p.get_address_list.assert_called_once_with(None)
	mock_attach.to_s.assert_called_once_with()
