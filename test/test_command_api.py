import sys
import os
from nose.tools import *
import vs2007
from vs2007.process import VS2007Process
from vs2007.command_api import main, _parse_options
from mock import MagicMock

saved = None

def setup():
	global saved
	saved = sys.argv

def teardown():
	sys.argv = saved

def setup_mocks():
	vs2007._VS2007Process = vs2007.process.VS2007Process
	global mock_vs2007p
	mock_vs2007p = MagicMock(return_value = None)
	vs2007.process.VS2007Process = MagicMock(return_value = mock_vs2007p)

def teardown_mocks():
	vs2007.process.VS2007Process = vs2007._VS2007Process
	delattr(vs2007, '_VS2007Process')

def test_help():
	sys.argv = ['vs-api', '--help']
	assert_raises(SystemExit, _parse_options)


def test_options():
	sys.argv = ['vs2007api', '--verbose', 'TEST_CMD']
	(options, args) = _parse_options()
	assert options.verbose
	assert args == ['TEST_CMD']

@with_setup(setup_mocks, teardown_mocks)
def test_get_handle_return_handle():
	sys.argv = ['vs2007api', '-g']
	vs2007.process.VS2007Process.get_handle = MagicMock(return_value = 100)
	assert_raises(SystemExit, main)
	vs2007.process.VS2007Process.get_handle.assert_called_once_with()

@with_setup(setup_mocks, teardown_mocks)
def test_set_handle():
	sys.argv = ['vs2007api', '-d', '12445']
	main()
	vs2007.process.VS2007Process.set_handle.assert_called_once_with(12445)

@with_setup(setup_mocks, teardown_mocks)
def test_set_handle():
	sys.argv = ['vs2007api', 'TEST_CMD']
	main()
	mock_vs2007p.send_command.assert_called_once_with('TEST_CMD')

