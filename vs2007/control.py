#!/usr/bin/env python
try:
	from vs2007 import VS2007Process
except ImportError:
	pass

import shlex, subprocess
import time
import os
import sys
import imp
import psutil
import re
import win32ui, win32api, ctypes
from optparse import OptionParser
import argparse
from ctypes import wintypes
import struct
global exe_name
global exe_path
global program_dirs
exe_name = 'VS2007.exe'
program_dirs = ['C:\\Program Files (x86)', 'C:\\Program Files']
global PROCESS_ALL_ACCESS
PROCESS_ALL_ACCESS = 0x1F0FFF
global rPM
rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
rPM.restype = wintypes.BOOL

def main_is_frozen():
	return (hasattr(sys, 'frozen') or hasattr(sys, 'importers') or imp.is_frozen("__main__"))

def get_main_path():
	if main_is_frozen():
		return os.path.dirname(sys.executable)
	return os.path.dirname(os.path.realpath(__file__))

def get_exe_path():
	for dir in [ os.path.join(dir, 'VS2007') for dir in program_dirs]:
		path = os.path.join(dir, exe_name)
		if os.path.exists(path):
			return os.path.realpath(path)

def on_terminate(proc):
	print "SUCCESS"
    #pass
    #print ("process {} terminated".format(proc))

def stop():
	pid = get_pid()
	if pid == None:
		print "%s is not running" % exe_name
		return
#	print "stopping %s..." % exe_name
	proc = psutil.Process(pid)
	proc.terminate()
	gone, alive = psutil.wait_procs([proc], timeout = 5, callback=on_terminate)
	for p in alive:
		p.kill()

def start():
	pid = get_pid()
	if not pid == None:
		print "%s is already running (PID: %d)" % (exe_name, pid)
		return
	#print "starting %s..." % exe_name
	exe_path = get_exe_path().replace('\\','/')

	command_line = "%s" % (exe_path)
	args = shlex.split(command_line)
	pp = subprocess.Popen(args)
	first_time = time.time()
	last_time = first_time
	while True:
		new_time = time.time()
		pid = get_pid()
		if not pid == None:
			break
		if new_time - first_time > timeout:
			break
		time.sleep(0.5)
	if not pid == None:
		print "SUCCESS %d" % pid
		return pid
	else:
		print "FAILED"
		return

def get_pid():
    for pid in psutil.get_pid_list():
        p = psutil.Process(pid)
        try:
            if p.name() == exe_name:
                return pid
        except psutil.AccessDenied:
            pass

def get_strings(ADDRESS, SIZE, pid = get_pid()):
	ADDRESS2 = ctypes.create_string_buffer(SIZE)
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS, ADDRESS2,SIZE,ctypes.byref(bytes_read))
	return ADDRESS2.value

def read_string_from_process_memory(pid, address0):
	PROCESS_ALL_ACCESS = 0x1F0FFF
	SIZE = 260
	ADDRESS2 = ctypes.create_string_buffer(SIZE)
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS, 0, pid)
	rPM(process.handle, address0, ADDRESS2, SIZE, ctypes.byref(bytes_read))
	return ADDRESS2.value

def get_version(pid = get_pid()):
	ADDRESS0 = 0x00475A48
	SIZE = 260
	ADDRESS2 = ctypes.create_string_buffer(SIZE)
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS0, ADDRESS2,SIZE,ctypes.byref(bytes_read))
	return ADDRESS2.value


def get_path(pid = get_pid()):
	ADDRESS0 = 0x0046CD58
	SIZE = 260
	ADDRESS2 = ctypes.create_string_buffer(SIZE)
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS0, ADDRESS2,SIZE,ctypes.byref(bytes_read))
	return ADDRESS2.value

def get_dataname(pid = get_pid()):
	ADDRESS1 = 0x0046CE5D	
	SIZE = 260
	ADDRESS2 = ctypes.create_string_buffer(SIZE)
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS1, ADDRESS2,SIZE,ctypes.byref(bytes_read))
	return ADDRESS2.value

def get_address(ADDRESS1, pid = get_pid()):

	bytes_read = ctypes.c_size_t()
	address = ctypes.c_ulong()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS1, ctypes.byref(address),ctypes.sizeof(address),ctypes.byref(bytes_read))

	return address.value

def get_value(ADDRESS, buf = ctypes.c_ulong(), pid = get_pid()):
	bytes_read = ctypes.c_size_t()
	process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)
	rPM(process.handle, ADDRESS, ctypes.byref(buf),ctypes.sizeof(buf),ctypes.byref(bytes_read))

	return buf.value


def pwd():
	pid = get_pid()
	if not (pid == None) and (get_value(0x476c78, ctypes.c_ulong()) == 1):
		path = os.path.join(get_path(),get_dataname())
		print os.path.abspath(path)

def get_address_data(base_adr):
	data = get_strings(base_adr + 0x70, 200)
	y = get_value(base_adr + 0x68, ctypes.c_double())
	x = get_value(base_adr + 0x60, ctypes.c_double())
	name = get_strings(base_adr + 0x44, 20)
	class_id = get_value(base_adr + 0x40, ctypes.c_ulong())
	address_id = get_value(base_adr + 0x3C, ctypes.c_ulong())
	dic = {'address_id':int(address_id), 'class_id':int(class_id)}
	dic['name'] = name
	dic['locate_x'] = x
	dic['locate_y'] = y
	dic['data'] = data
	return dic

def get_attach_data(base_adr):
	class_id = get_value(base_adr + 0x460, ctypes.c_ulong())
	attach_id = get_value(base_adr + 0x430, ctypes.c_ulong())
	dic = {'attach_id':int(attach_id), 'class_id':int(class_id)}
	dic['name'] = get_strings(base_adr + 0x434, 20)
	dic['file'] = get_strings(base_adr + 0x449, 20)
	if not (class_id == 0):
		dic['locate_y'] = get_value(base_adr + 0x470, ctypes.c_double())
		dic['locate_x'] = get_value(base_adr + 0x468, ctypes.c_double())
		dic['imag'] = int(get_value(base_adr + 0x478, ctypes.c_ulong()))
		dic['center_x'] = get_value(base_adr + 0x490, ctypes.c_double())
		dic['center_y'] = get_value(base_adr + 0x4B8, ctypes.c_double())
		dic['size_x'] = get_value(base_adr + 0x498, ctypes.c_double())
		#print get_value(base_adr + 0x4A8, ctypes.c_double())
		dic['size_y'] = get_value(base_adr + 0x4C0, ctypes.c_double())
		#print get_value(base_adr + 0x4D0, ctypes.c_double())

	return dic
	#print "%d,%d,%s,%.3f,%.3f,%s" % (address_id, class_id, name, x, y, data)

def get_attachlist(base_adr):
	address_id = get_value(base_adr + 0x3C, ctypes.c_ulong())
	start_adr = get_value(base_adr + 0x4E98)
	if start_adr == 0:
		return
	current_adr = start_adr
	while True:
		prev_adr = get_address(current_adr)
		next_adr = get_address(current_adr + 4)
#		print "curr: %x prev: %x next: %x" % (current_adr, prev_adr, next_adr)
		base_adr = current_adr
		base_adr += 0x10
		flag = get_value(base_adr, ctypes.c_ulong())

		flag = flag & 0x4
		if flag == 0:
			dic_attach = get_attach_data(base_adr)
			line = "%d\t%d\t%d\t%s\t%s" % (address_id,dic_attach['attach_id'],dic_attach['class_id'],dic_attach['name'],dic_attach['file'])
			if not dic_attach['class_id'] == 0:
				line += "\t%.3f\t%.3f" % (dic_attach['locate_x'],dic_attach['locate_y'])
				line += "\t%.3f\t%.3f" % (dic_attach['center_x'],dic_attach['center_y'])
				line += "\t%.3f\t%.3f" % (dic_attach['size_x'],dic_attach['size_y'])
				line += "\t%d" % (dic_attach['imag'])
			print line

		if next_adr == 0:
			break

		current_adr = next_adr

def address_list(iid = None, pid = get_pid()):
	#See 0x00417439
	if pid == None:
		print "STOPPED"
	else:
		start_address = get_address(0x00477060)		
		current_adr = start_address
		while True:
			prev_adr = get_address(current_adr)
			next_adr = get_address(current_adr + 4)
			#print "curr: %x prev: %x next: %x" % (current_adr, prev_adr, next_adr)
			
			base_adr = current_adr
			base_adr += 0x10
			flag = get_value(base_adr, ctypes.c_ulong())
			address_id = get_value(base_adr + 0x3C, ctypes.c_ulong())
			flag = flag & 0x4
			if flag == 0:
				if iid == None or address_id == iid:
					dic_addr = get_address_data(base_adr)
					print "%d\t%d\t%s\t%.3f\t%.3f\t%s" % (dic_addr['address_id'], dic_addr['class_id'], dic_addr['name'], dic_addr['locate_x'], dic_addr['locate_y'], dic_addr['data'])

#				get_attachlist(base_adr)
			if next_adr == 0:
				break
			current_adr = next_adr

def attach_list(iid = None, pid = get_pid()):
	if pid == None:
		print "STOPPED"
	else:
		start_address = get_address(0x00477060)		
		current_adr = start_address
		while True:
			prev_adr = get_address(current_adr)
			next_adr = get_address(current_adr + 4)
			#print "curr: %x prev: %x next: %x" % (current_adr, prev_adr, next_adr)
			
			base_adr = current_adr
			base_adr += 0x10
			flag = get_value(base_adr, ctypes.c_ulong())
			address_id = get_value(base_adr + 0x3C, ctypes.c_ulong())

			flag = flag & 0x4
			if flag == 0:
				if iid == None or address_id == iid:
					get_attachlist(base_adr)


			if next_adr == 0:
				break
			current_adr = next_adr

def inject_dll():
	if pid == None:
		print "STOPPED"
	else:
		dll_path = os.path.realpath(os.path.join(main_path, '../lib/vs2007_orochi/Release/vs2007_orochi.dll')).replace('\\','/')
		dll_len = len(dll_path)
		PAGE_READWRITE = 0x04
		PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
		VIRTUAL_MEM = (0x1000 | 0x2000)

		kernel32 = ctypes.windll.kernel32

		h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))

		if not h_process:
			print "[*] Couldn't acquire a handle to PID: %s" % pid
			sys.exit(0)

		arg_address = kernel32.VirtualAllocEx(h_process, 0, dll_len, VIRTUAL_MEM, PAGE_READWRITE)

		written = ctypes.c_int(0)
		kernel32.WriteProcessMemory(h_process, arg_address, dll_path, dll_len, ctypes.byref(written))

		h_kernel32 = kernel32.GetModuleHandleA("kernel32.dll")
		h_loadlib = kernel32.GetProcAddress(h_kernel32, "LoadLibraryA")

		thread_id = ctypes.c_ulong(0)
		if not kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, ctypes.byref(thread_id)):
			print "[*] Failed to inject the DLL. Exiting."
			sys.exit(0)

		print "[*] Remote thread with ID 0x%08x created." % thread_id.value

def _start(args):
	VS2007Process.start()

def _stop(args):
	VS2007Process.stop()

def _parse_options():
#	parser = OptionParser("usage: %prog [options] (start|stop|restart|status|inject|pwd|export <address|attach>)")
#	parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
#	(options, args) = parser.parse_args()
#	if not len(args) >= 1:
#	    parser.error("incorrect number of arguments")
#	    sys.exit()
#	command = args.pop(0)
#	return options, command, args
	parser = argparse.ArgumentParser(prog='vs2007')
	parser.add_argument('--verbose', action='store_true', help='make lots of noise')
	subparsers = parser.add_subparsers(dest='subparser_name')

	parser_start = subparsers.add_parser('start')
	parser_start.set_defaults(func=_start)

	parser_start = subparsers.add_parser('stop')
	parser_start.set_defaults(func=_stop)

	args = parser.parse_args()
	return args

def main():
	args = _parse_options()
	args.func(args)
#	sys.exit()

def main_old():
	exe_path = get_exe_path().replace('\\','/')

	if exe_path == None:
		print "could not find %s" % exe_name
		sys.exit(1)
	main_path = get_main_path()

	parser = OptionParser("usage: %prog [options] (start|stop|restart|status|inject|pwd|export <address|attach>)")
	parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
	#    parser.add_option("-i","--interactive",action="store_true",dest="interactive",default=True,help="interactive mode")
	#parser.add_option("-t","--timeout",action="store",type="int",dest="timeout",default=0,help="specify timeout (ms)")
	# parser.add_option("-d","--set_handle",action="store",type="int",dest="handle",default=0,help="specify window handle of VisualStage")
	#parser.add_option("-w","--window",action="store_true",dest="window",default=False,help="start the application with window")    

	#rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
	#rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
	#rPM.restype = wintypes.BOOL
	#PROCESS_ALL_ACCESS = 0x1F0FFF


	(options, args) = parser.parse_args()
	if not len(args) >= 1:
	    parser.error("incorrect number of arguments")
	    sys.exit()

	pid = get_pid()

	command = args[0]
	if command == 'start':
		pid = start()
	elif command == "stop":
		stop()
	elif command == "inject":
		inject_dll()
	elif command == "export":
		if len(args) > 1:
			iid = None
			command = args[1]
			if len(args) > 2:
				iid = int(args[2])

			if command == 'attach':
				attach_list(iid)
			else:
				address_list(iid)
		else:
			address_list()
	elif command == "pwd":
		pwd()
	elif command == "status":
		pid = get_pid()
		if not pid == None:
			print "RUNNING %d" % pid
		else:
			print "STOPPED"
	elif command == "restart":
		pid = get_pid()
		if not pid == None:
			stop()
		start()
	else:
	    parser.error("%s is incorrect argument" % command)
	    sys.exit()

	sys.exit()

if __name__ == '__main__':
	main()