import os
import shlex
import re 
import subprocess
import time
import psutil
import ctypes
import win32api
import ntpath
import logging
import yaml
from ctypes import wintypes
from vs2007.api import VS2007API
from vs2007.medusa import VS2007Medusa
from vs2007 import Address
from vs2007 import Attach

class VS2007Process(object):
	exe_name = 'VS2007.exe'
	program_dirs = ['C:\\Program Files (x86)', 'C:\\Program Files']
	program_subdirname = 'VS2007'
	pid = None

	dic_address_for = {
		'open_flag': {'1.100': 0x476C78, '1.120': 0x00479D28},
		'path': {'1.100': 0x0046CD58, '1.120': 0x0046FE08},
		'dataname': {'1.100': 0x0046CE5D, '1.120': 0x0046FF0D},
		'addresslist': {'1.100': 0x00477060, '1.120': 0x0047A120}
	}

	PROCESS_ALL_ACCESS = 0x1F0FFF
	rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
	rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
	rPM.restype = wintypes.BOOL

	@classmethod
	def get_exe_path(cls):
		for dir in [ os.path.join(dir, cls.program_subdirname) for dir in cls.program_dirs]:
			path = os.path.join(dir, cls.exe_name)
			if os.path.exists(path):
				realpath = os.path.realpath(path)
				return realpath.replace('\\', '/')

	@classmethod
	def is_running(cls):
		logging.info('VS2007Process.is_running')
		if cls.pid == None:
			logging.info('VS2007Process.pid is None')
			pid = cls.get_pid()
			return not pid == None
		else:
			logging.info('VS2007Process.pid is %d' % cls.pid)
			return cls.check_pid(cls.pid)
		#pid = cls.get_pid()
		#return not pid == None

	@classmethod
	def start(cls, timeout = 50):
		logging.info('VS2007Process.start')
		pid = cls.get_pid()
		if not pid == None:
			logging.warn("%s is already running (PID: %d)" % (cls.exe_name, pid))
			return pid
		else:
			logging.info('%s is not running' % cls.exe_name)

		if not VS2007API.g_hVSWnd == None:
			logging.warn('VS2007API.g_hVSWnd is not None')
			VS2007API.g_hVSWnd = None

		exe_path = cls.get_exe_path()
		command_line = "%s" % (exe_path)
		args = shlex.split(command_line)
		logging.info('starting %s...' % command_line)
		pp = subprocess.Popen(args)
		first_time = time.time()
		last_time = first_time
		cnt = 0
		while True:
			cnt += 1
			new_time = time.time()
			pid = cls.get_pid()
			if not pid == None:
				#logging.info('(%d) PID: %d' % (cnt, pid))
				break
			d_time = new_time - first_time
			logging.warn('(%d) d_time %d timeout %d' % (cnt, d_time, timeout))
			if d_time > timeout:
				logging.warn('timeout')
				break
			time.sleep(0.5)
			if not pid == None:
				print("SUCCESS %d" % pid)
				return pid
			elif cnt > 10:
				print("FAILED")
				return

	@classmethod
	def stop(cls):
		logging.info('VS2007Process.stop')
		def on_terminate(proc):
			logging.info("%s is stopped." % cls.exe_name)
			cls.pid = None
			if not VS2007API.g_hVSWnd == None:
				VS2007API.g_hVSWnd = None
		

		pid = cls.get_pid()
		if pid == None:
			logging.warn("%s is not running" % cls.exe_name)
			return
		else:
			logging.info("%s is running (PID: %d)" % (cls.exe_name, pid))

		logging.info('stopping %s (PID: %d)...' % (cls.exe_name, pid))
		try:
			proc = psutil.Process(pid)
			proc.terminate()
			gone, alive = psutil.wait_procs([proc], timeout = 15, callback=on_terminate)
			for p in alive:
				p.kill()
		except psutil.NoSuchProcess as e:
			return

	@classmethod
	def _drive_with_path(cls, drive = 'C', path = ''):
		return drive.upper() + ':\\' + path

	@classmethod
	def _ntpath(cls, path):
		p = re.compile('/cygdrive/([A-Za-z])/(.+)')
		m = p.match(path)
		if m:
			path = cls._drive_with_path(m.group(1), m.group(2))
			#drive = m.group(1)
			#path = drive + ':\\' + m.group(2)

		p = re.compile('/([A-Za-z])/(.+)')
		m = p.match(path)
		if m:
			path = cls._drive_with_path(m.group(1), m.group(2))
			#drive = m.group(1)
			#path = drive + ':\\' + m.group(2)

		return ntpath.abspath(path)

	@classmethod
	def check_pid(cls, pid):
		logging.info('VS2007Process.check_pid...')
		try:
			p = psutil.Process(pid)
			cnt = 0
			if p.name() == cls.exe_name:
				logging.info('(%d) pid: %d [%s]' % (cnt, pid, cls.exe_name))
				return True
		except psutil.NoSuchProcess:
			logging.info('NoSuchProcess')
			return False
		#except psutil.AccessDenied:
		#	pass


	@classmethod
	def get_pid(cls):
		logging.info('VS2007Process.get_pid...')
		if not cls.pid == None:
			return cls.pid
		cnt = 0
		for pid in psutil.pids():
			cnt += 1
			try:
				p = psutil.Process(pid)
				if p.name() == cls.exe_name:
					logging.info('(%d) pid: %d [%s]' % (cnt, pid, cls.exe_name))
					cls.pid = pid
					return pid
			except psutil.NoSuchProcess:
				pass
			except psutil.AccessDenied:
				pass

	@classmethod
	def set_pid(cls, pid):
		logging.info('VS2007Process.set_pid %d' % pid)
		cls.pid = pid

	@classmethod
	def get_handle(cls, timeout = 1000):
		logging.info("get_handle...\n")
		api = VS2007API(None, timeout)
		return api.g_hVSWnd

	@classmethod
	def set_handle(cls, handle):
		logging.info('VS2007Process.set_handle %d' % handle)
		api = VS2007API(handle)
		VS2007API.set_handle(handle)

	def __new__(cls, *args, **kw):
		if not hasattr(cls, '_instance'):
			orig = super(VS2007Process, cls)
			cls._instance = orig.__new__(cls, *args, **kw)
		return cls._instance

	def __init__(self, *args, **kw):
		#pass
		#self.pid = self.get_pid()
		#self.process = win32api.OpenProcess(self.PROCESS_ALL_ACCESS,0,self.pid)
		self._pid = None
		self._version = None
		self._process = None
		self._api = None
		self._medusa_api = None
		self._timeout = 50
		#if 'timeout' in kw:
		#	print(kw['timeout'])
		#	self.timeout = kw['timeout']
			
		#self.api = VS2007API()

	def send_command(self, command, timeout = 0):
		self.timeout = timeout
		if self.api:
			return self.api.send_command_and_receive_message(command, self.timeout)

	def address_for(self, key):
		dic = self.dic_address_for[key]
		if dic:
			return dic[self.version]

	def _get_version(self):
		if self._version == None:
			version = self.read_string_from_process_memory(0x00475A48)
			if version == b'':
				version = self.read_string_from_process_memory(0x00478AF8)
			self._version = version
		return self._version.decode("UTF-8")

	def _set_version(self, value):
		print("_set_version...")
		self._version = value

	version = property(_get_version, _set_version)

	def _get_pid(self):
		logging.info('_get_pid')
		if self._pid == None:
			self._pid = self.get_pid()

		return self._pid

	def _set_pid(self, value):
		self._pid = value

	#pid = property(_get_pid, _set_pid)

	def _get_process(self):
		if self._process == None:
			self._process = win32api.OpenProcess(self.PROCESS_ALL_ACCESS,0,self.pid)
		return self._process

	def _set_process(self, value):
		self._process = value

	process = property(_get_process, _set_process)

	def _get_api(self):
		logging.debug('VS2007Process._get_api')
		if self._api == None:
			logging.debug('_api is None')
			self._api = VS2007API(None, self.timeout)
		return self._api

	def _set_api(self, value):
		self._api = value

	api = property(_get_api, _set_api)


	def _get_medusa_api(self):
		logging.debug('VS2007Process._get_medusa_api')
		if self._medusa_api == None:
			logging.debug('_medusa_api is None')
			self._medusa_api = VS2007Medusa()
		return self._medusa_api

	def _set_medusa_api(self, value):
		self._medusa_api = value
	
	medusa_api = property(_get_medusa_api, _set_medusa_api)

	def _get_timeout(self):
		return self._timeout

	def _set_timeout(self, value):
		self._timeout = value

	timeout = property(_get_timeout, _set_timeout)

	def file_open(self, path, flag = False):
		path = self._ntpath(path)
#		if os.path.isabs(path):
#			path = os.path.abspath(path)
		if os.path.isdir(path):
			path = os.path.join(path, 'ADDRESS.DAT')

		if not os.path.isfile(path):
			raise ValueError("invalid path")

		dirname = os.path.dirname(path)
		datadir = os.path.dirname(dirname)
		dataname = os.path.basename(dirname)
		command = "FILE_OPEN %s,%s,%s" % (datadir, dataname, 'YES' if flag else 'NO')
		return self.api.send_command_and_receive_message(command)
	
	def file_save(self):
		command = 'FILE_SAVE'
		return self.api.send_command_and_receive_message(command)		

	def file_close(self, flag = False):		
		command = "FILE_CLOSE %s" % ('YES' if flag else 'NO')
		return self.api.send_command_and_receive_message(command)


	def get_value(self, ADDRESS, buf = ctypes.c_ulong()):
		bytes_read = ctypes.c_size_t()
		self.rPM(self.process.handle, ADDRESS, ctypes.byref(buf),ctypes.sizeof(buf),ctypes.byref(bytes_read))
		return buf.value

	def read_string_from_process_memory(self, address0):
		SIZE = 260
		ADDRESS2 = ctypes.create_string_buffer(SIZE)
		bytes_read = ctypes.c_size_t()
		self.rPM(self.process.handle, address0, ADDRESS2, SIZE, ctypes.byref(bytes_read))
		return ADDRESS2.value


	def is_file_opened(self):
		logging.info('is_file_opened')
		return self.get_value(self.address_for('open_flag'), ctypes.c_ulong()) == 1		

	def pwd(self):
		logging.info('pwd')
		logging.info(self.pid)
		if not (self.pid == None) and self.is_file_opened:
			path = os.path.join(self.get_path(), self.get_dataname())
			return os.path.abspath(path)

	def get_path(self):
		return self.read_string_from_process_memory(self.address_for('path')).decode('utf-8')

	def get_dataname(self):
		logging.debug('VS2007Process#get_dataname')
		logging.debug(self.address_for('dataname'))
		string = self.read_string_from_process_memory(self.address_for('dataname')).decode('utf-8')
		logging.debug(string)
		return string

	def get_address(self, ADDRESS1):
#		pid = cls.get_pid()
		bytes_read = ctypes.c_size_t()
		address = ctypes.c_ulong()
#		process = win32api.OpenProcess(cls.PROCESS_ALL_ACCESS,0,pid)
#		rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
#		rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
#		rPM.restype = wintypes.BOOL
		self.rPM(self.process.handle, ADDRESS1, ctypes.byref(address),ctypes.sizeof(address),ctypes.byref(bytes_read))
		return address.value

	def get_strings(self, ADDRESS, SIZE):
		#pid = cls.get_pid()
		ADDRESS2 = ctypes.create_string_buffer(SIZE)
		bytes_read = ctypes.c_size_t()
		#process = win32api.OpenProcess(cls.PROCESS_ALL_ACCESS,0,pid)
	#rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
	#rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
	#rPM.restype = wintypes.BOOL
	#PROCESS_ALL_ACCESS = 0x1F0FFF

		self.rPM(self.process.handle, ADDRESS, ADDRESS2,SIZE,ctypes.byref(bytes_read))
		return ADDRESS2.value.decode()


	def get_address_data(self, base_adr):
		data = self.get_strings(base_adr + 0x70, 200)
		y = self.get_value(base_adr + 0x68, ctypes.c_double())
		x = self.get_value(base_adr + 0x60, ctypes.c_double())
		name = self.get_strings(base_adr + 0x44, 20)
		class_id = self.get_value(base_adr + 0x40, ctypes.c_ulong())
		address_id = self.get_value(base_adr + 0x3C, ctypes.c_ulong())
		dic = {'address_id':int(address_id), 'class_id':int(class_id)}
		dic['name'] = '"' + name + '"'
		dic['locate_x'] = x
		dic['locate_y'] = y
		dic['data'] = '"' + data + '"'
		return dic

	def get_attach_data(self, base_adr):
		class_id = self.get_value(base_adr + 0x460, ctypes.c_ulong())
		attach_id = self.get_value(base_adr + 0x430, ctypes.c_ulong())
		dic = {'attach_id':int(attach_id), 'class_id':int(class_id)}
		dic['name'] = self.get_strings(base_adr + 0x434, 20)
		dic['file'] = self.get_strings(base_adr + 0x449, 20)
		if not (class_id == 0):
			dic['locate_y'] = self.get_value(base_adr + 0x470, ctypes.c_double())
			dic['locate_x'] = self.get_value(base_adr + 0x468, ctypes.c_double())
			dic['imag'] = int(self.get_value(base_adr + 0x478, ctypes.c_ulong()))
			dic['center_x'] = self.get_value(base_adr + 0x490, ctypes.c_double())
			dic['center_y'] = self.get_value(base_adr + 0x4B8, ctypes.c_double())
			dic['size_x'] = self.get_value(base_adr + 0x498, ctypes.c_double())
		#print get_value(base_adr + 0x4A8, ctypes.c_double())
			dic['size_y'] = self.get_value(base_adr + 0x4C0, ctypes.c_double())
		#print get_value(base_adr + 0x4D0, ctypes.c_double())
		return dic


	def get_address_list(self, iid = None):
		base_dir = self.pwd()
		addresslist = []
		#See 0x00417439
		pid = self.pid
		if pid == None:
			print("STOPPED")
		else:
			#start_address = self.get_address(0x00477060)
			start_address = self.get_address(self.address_for('addresslist'))					
			current_adr = start_address
			while True:
				prev_adr = self.get_address(current_adr)
				next_adr = self.get_address(current_adr + 4)
				#print("curr: %x prev: %x next: %x" % (current_adr, prev_adr, next_adr))
		
				base_adr = current_adr
				base_adr += 0x10
				flag = self.get_value(base_adr, ctypes.c_ulong())
				address_id = self.get_value(base_adr + 0x3C, ctypes.c_ulong())
				flag = flag & 0x4
				if flag == 0:
					if iid == None or address_id == iid:
						dic_addr = self.get_address_data(base_adr)
						addr = Address(dic_addr)
						#print "%d\t%d\t%s\t%.3f\t%.3f\t%s" % (dic_addr['address_id'], dic_addr['class_id'], dic_addr['name'], dic_addr['locate_x'], dic_addr['locate_y'], dic_addr['data'])
						addr.attachlist = self.get_attachlist(base_adr, base_dir)
						addresslist.append(addr)

				if next_adr == 0:
					break
				current_adr = next_adr
			return addresslist

	def get_attachlist(self, base_adr, base_dir):
		attachlist = []
		address_id = self.get_value(base_adr + 0x3C, ctypes.c_ulong())
		start_adr = self.get_value(base_adr + 0x4E98)
		if start_adr == 0:
			return
		current_adr = start_adr
		while True:
			prev_adr = self.get_address(current_adr)
			next_adr = self.get_address(current_adr + 4)
#		print "curr: %x prev: %x next: %x" % (current_adr, prev_adr, next_adr)
			base_adr = current_adr
			base_adr += 0x10
			flag = self.get_value(base_adr, ctypes.c_ulong())

			flag = flag & 0x4
			if flag == 0:
				dic_attach = self.get_attach_data(base_adr)
				obj = Attach(dic_attach, base_dir = base_dir)
				obj.address_id = address_id
				attachlist.append(obj)
				#line = "%d\t%d\t%d\t%s\t%s" % (address_id,dic_attach['attach_id'],dic_attach['class_id'],dic_attach['name'],dic_attach['file'])
				#if not dic_attach['class_id'] == 0:
				#	line += "\t%.3f\t%.3f" % (dic_attach['locate_x'],dic_attach['locate_y'])
				#	line += "\t%.3f\t%.3f" % (dic_attach['center_x'],dic_attach['center_y'])
				#	line += "\t%.3f\t%.3f" % (dic_attach['size_x'],dic_attach['size_y'])
				#	line += "\t%d" % (dic_attach['imag'])
				#print line

			if next_adr == 0:
				break

			current_adr = next_adr
		return attachlist

	def remote_import(self, path, surface_name, flag = False):
		logging.info("remote_import")
		logging.info("VS-DIR %s SURFACE:%s" %(path, surface_name))
		if self.file_open(path) == "SUCCESS":
			_wapi = self.medusa_api
			spots = []
			attachs = []
			addrl = self.get_address_list()
			for addr in addrl:
				#spots.append(addr.to_spot()) 
				for attach in addr.get_attachlist():
					if ((not attach.what() == None) and (not attach.is_cropped()) and (not attach.is_warped())):
						attachs.append(attach)
					#print(attach.to_s())
			surface = _wapi.create_surface(surface_name, addrs=addrl, attachs=attachs)
			#surface = {'id': 79}


	def checkout(self, surface_id, path, flag = False):
		logging.info("checkout")
		logging.info("SURFACE-ID: %s VS-DIR:%s" %(surface_id, path))
		_wapi = self.medusa_api

		path = self._ntpath(path)
		datadir = os.path.dirname(path)
		dataname = os.path.basename(path)
		config_path = os.path.join(path, "vs.config")
		export_path = os.path.join(path, "exported.txt")
		import_path = os.path.join(path,"imported.txt")

		command = "FILE_NEW %s,%s,%s" % (datadir, dataname, 'YES' if flag else 'NO')
		r_vs = self.api.send_command_and_receive_message(command)
		if (r_vs == 'SUCCESS'):
			record = _wapi.get_record(surface_id)
			if (record['datum_type'] == 'Surface'):
				with open(config_path, 'w') as config_file:
					yaml.safe_dump({'surface_id': surface_id}, config_file)
				spots = _wapi.get_spots(record['datum_id'])
				logging.info("writing %s" % import_path)
				with open(import_path, 'w') as import_file:
					import_file.write('\t'.join(["Class", "Name", "X-Locate", "Y-Locate", "Data"]) + '\n')
					for spot in spots:
						import_file.write('\t'.join(["0", spot['name'], str(spot['world_x']),  str(spot['world_y']), spot['global_id']]) + '\n')
				command = "FILE_IMPORT %s" % (import_path)
				r_vs = self.api.send_command_and_receive_message(command)
				

