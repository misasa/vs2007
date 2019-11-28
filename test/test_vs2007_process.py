import sys
import os
import shutil
import ntpath
import time
import unittest
from nose.tools import *
from mock import MagicMock
from testfixtures import LogCapture
import logging
import vs2007
from vs2007.process import VS2007Process
from vs2007.api import VS2007API
#from vs2007.control import *

vs2007p = VS2007Process()

def start_vs():
	VS2007Process.start()

def stop_vs():
	VS2007Process.stop()

# py -m nose test.test_vs2007_process
class TestWithMockAPICase:
	def setup(self):
		vs2007p.api.send_command_and_receive_message = MagicMock(return_value = 'SUCCESS')

	def test_open_file_with_full_dirpath(self):
		path = 'C:\\VS2007data'
		dataname = 'GrtCCG06'
		message = vs2007p.file_open(os.path.join(path, dataname))
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,NO')

	def test_save_file(self):
		print(vs2007p)
		#message = vs2007p.file_save()
		#vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_SAVE')

	def test_open_file_with_full_filepath(self):
		path = 'C:\\VS2007data'
		dataname = 'GrtCCG06'
		message = vs2007p.file_open(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

	def test_open_file_with_full_cygpath(self):
		path = '/cygdrive/c/VS2007data'
		dataname = 'GrtCCG06'
		message = vs2007p.file_open(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

	def test_open_file_with_full_msyspath(self):
		path = '/c/VS2007data'
		dataname = 'GrtCCG06'
		message = vs2007p.file_open(os.path.join(path, dataname, 'ADDRESS.DAT'), True)
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_OPEN C:\\VS2007data,GrtCCG06,YES')

	def test_open_file_with_invalid_path(self):
		path = 'C:\\InvalidPath'
		dataname = 'GrtCCG06'
		assert_raises(ValueError, vs2007p.file_open, os.path.join(path, dataname, 'ADDRESS.DAT'), True)
	
	def test_close_file(self):
		message = vs2007p.file_close()
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_CLOSE NO')

	def test_close_file_with_flag(self):
		message = vs2007p.file_close(True)
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_CLOSE YES')

	def test_save_file(self):
		message = vs2007p.file_save()
		vs2007p.api.send_command_and_receive_message.assert_called_once_with('FILE_SAVE')

	def teardown(self):
		pass

class WithTmpCase:
	def __init__(self):
		self.tmp_dir = ntpath.abspath("./tmp")	

	def setup(self):
		if os.path.exists(self.tmp_dir):
			shutil.rmtree(self.tmp_dir)
		os.mkdir(self.tmp_dir)

	def test_checkout(self):
		surface_id = '20190903141611-024227'
		path = './tmp/test-vs-1'
		logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
		logger = logging.getLogger('')
		with LogCapture() as logs:
			os.path.exists(path)
			VS2007Process().checkout(surface_id, path)
			#print(str(logs))

	def teardown(self):
		#if os.path.exists(self.tmp_dir):
		#	shutil.rmtree(self.tmp_dir)	
		pass
# py -m nose test.test_vs2007_process:WithVSCase
class WithVSCase:
	def setup(self):
		start_vs()

	def test_get_path_and_dataname(self):
		path = 'C:\\VS2007data'
		dataname = 'GrtCCG06'
		command = "FILE_OPEN %s,%s,YES" % (path, dataname)
		assert_equal(VS2007Process().api.send_command_and_receive_message(command, 0), 'SUCCESS')
		assert_equal(VS2007Process().get_path(), path + '\\')
		assert_equal(VS2007Process().get_dataname(), dataname)	
		assert_equal(VS2007Process().pwd(), path + '\\' + dataname)
		addrl = VS2007Process().get_address_list()
		assert len(addrl) > 0
		assert len(addrl[0].get_attachlist()) > 0
		for addr in addrl:
			print(addr.to_s())
		for addr in addrl:
			for attach in addr.get_attachlist():
				print(attach.to_s())

	def test_is_running(self):
		assert_equal(VS2007Process.is_running(), True)

	def test_get_handle(self):
		logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
		logger = logging.getLogger('')
		with LogCapture() as logs:
			handle = VS2007Process.get_handle()
			assert_true(not handle == None)
			assert 'get_handle...' in str(logs)
			print(str(logs))

	def test_api(self):
		logging.basicConfig(level='INFO', format='%(asctime)s %(levelname)s:%(message)s')
		logger = logging.getLogger('')
		with LogCapture() as logs:
			#assert_equal(VS2007Process().api.send_command_and_receive_message('TEST_CMD', 0), 'SUCCESS')
			#assert_equal(VS2007Process().api.send_command_and_receive_message('FILE_OPEN C:\\VS2007data,image2vs,YES', 0), 'SUCCESS')
			#assert_equal(VS2007Process().api.send_command_and_receive_message('FILE_CLOSE YES', 10), 'SUCCESS')
			VS2007Process().send_command('FILE_OPEN C:\\VS2007data,GrtCCG06,YES', 5000)
			#assert_equal(VS2007Process(timeout = 0).send_command('FILE_CLOSE YES'), 'SUCCESS')
			print(str(logs))


	def teardown(self):
		#stop_vs()
		pass


# py -m nose test.test_vs2007_process:WithoutVSCase
class WithoutVSCase:
	def setup(self):
		stop_vs()

	def test_stop(self):
		assert_equal(VS2007Process.is_running(), False)
