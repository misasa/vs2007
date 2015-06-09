import sys
import os
import unittest
from nose.tools import *
from mock import MagicMock
from vs2007 import VS2007Process
from vs2007 import VS2007API
from vs2007.control import *

saved = None
pid = None
vs2007p = None

def setup():
	global saved
	saved = sys.argv
	start_vs()
	global pid
	pid = get_pid()

def setup_112():
	global saved
	saved = sys.argv
	start_vs_112()
	global pid
	pid = get_pid()

def setup_mock_api():
	global original_api
	original_api = vs2007p.api.send_command_and_receive_message
	vs2007p.api.send_command_and_receive_message = MagicMock(return_value = 'SUCCESS' )	


def teardown_mock_api():
	vs2007p.api.send_command_and_receive_message = original_api


def teardown():
	stop_vs()
	sys.argv = saved

def start_vs():
	VS2007Process.program_subdirname = 'VS2007-1.120'
	global vs2007p
	VS2007Process.start()
	vs2007p = VS2007Process()

def stop_vs():
	VS2007Process.stop()

def test_api():
	command = 'TEST_CMD'
	message = vs2007p.api.send_command_and_receive_message(command, 0)
	assert_equal(message, 'SUCCESS')

def test_is_running():
	assert_equal(VS2007Process.is_running(), True)

@with_setup(setup_mock_api, teardown_mock_api)
def test_open_file_with_full_dirpath():
	path = 'C:\\VS2007data'
	dataname = 'GrtCCG06'
	message = vs2007p.open_file(os.path.join(path, dataname))
	vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,NO')
	#assert_equal(message, 'SUCCESS')

@with_setup(setup_mock_api, teardown_mock_api)
def test_open_file_with_full_filepath():
	path = 'C:\\VS2007data'
	dataname = 'GrtCCG06'
	message = vs2007p.open_file(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
	vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

@with_setup(setup_mock_api, teardown_mock_api)
def test_open_file_with_full_cygpath():
	path = '/cygdrive/c/VS2007data'
	dataname = 'GrtCCG06'
	message = vs2007p.open_file(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
	vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

@with_setup(setup_mock_api, teardown_mock_api)
def test_open_file_with_full_msyspath():
	path = '/c/VS2007data'
	dataname = 'GrtCCG06'
	message = vs2007p.open_file(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
	vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

@with_setup(setup_mock_api, teardown_mock_api)
def test_open_file_with_invalid_path():
	path = 'C:\\InvalidPath'
	dataname = 'GrtCCG06'
	assert_raises(ValueError, vs2007p.open_file, os.path.join(path, dataname, 'ADDRESS.DAT'), True)

def test_get_path_and_dataname():
#	VS2007Process.version = '1.120'
#	api = VS2007API()
	path = 'C:\\VS2007data'
	dataname = 'GrtCCG06'
	command = "FILE_OPEN %s,%s,NO" % (path, dataname)
	vs2007p.api.send_command_and_receive_message(command, 0)
	assert_equal(vs2007p.get_path(), path + '\\')
	assert_equal(vs2007p.get_dataname(), dataname)	
	assert_equal(vs2007p.pwd(), path + '\\' + dataname)

#@with_setup(None, teardown)
def test_get_addresslist_with_open():
	addrl = vs2007p.get_address_list()
	assert len(addrl) > 0
	assert len(addrl[0].attachlist) > 0

@with_setup(None, teardown)
def test_stop():
	pass

def test_is_running():
	assert_equal(VS2007Process.is_running(), False)