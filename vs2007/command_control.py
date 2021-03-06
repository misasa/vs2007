#!/usr/bin/env python
import vs2007
import vs2007.process
import vs2007.medusa
import argparse
import logging
from vs2007._version import __version__ as _version
_progname = 'vs'

def _process():
	p = vs2007.process.VS2007Process()
	return p

def _medusa():
	m = vs2007.medusa.VS2007Medusa()
	return m

def _start(args):
	pid = vs2007.process.VS2007Process.start()
	if pid:
		_output('SUCCESS %d' % pid)
	else:
		_output('FAILED')

def _stop(args):
	vs2007.process.VS2007Process.stop()

def _open(args):
	if not vs2007.process.VS2007Process.is_running():
		vs2007.process.VS2007Process.start()
	#vs2007p = vs2007.process.VS2007Process()
	_process().file_open(args.path)

def _close(args):
	if vs2007.process.VS2007Process.is_running():
		_process().file_close()		

def _save(args):
	if vs2007.process.VS2007Process.is_running():
		_process().file_save()

def _pwd(args):
	logging.info('_pwd...')
	if vs2007.process.VS2007Process.is_running():
		vs2007p = _process()
		pwd = vs2007p.pwd()
		print(pwd)

def _status(args):
	pid = vs2007.process.VS2007Process.get_pid()
	if pid:
		_output('RUNNING %d' % pid)
	else:
		_output('STOPPED')

def _list(args):
	if vs2007.process.VS2007Process.is_running():
		addrl = _process().get_address_list(args.index)
		for addr in addrl:		
			if args.address_or_attach == 'address':
				print(addr.to_s())
			elif args.address_or_attach == 'attach':
				for attach in addr.get_attachlist():
					print(attach.to_s())
def _import(args):
	if vs2007.process.VS2007Process.is_running():
		_process().remote_import(args.vs_dir, args.surface_name)

def _commit(args):
	if vs2007.process.VS2007Process.is_running():
		_process().remote_update(args.vs_dir, args.surface_name)

def _checkout(args):
	if vs2007.process.VS2007Process.is_running():
		_process().checkout(args.surface_id, args.vs_dir)

def _show_info(args):
	info = '%s %s' % (_progname, _version)
	if vs2007.process.VS2007Process.is_running():
		info += ' with VisualStage %s' % _process()._get_version()
	_output(info)

def _output(text):
	print(text)


def _parse_options():
	parser = argparse.ArgumentParser(prog='vs')
	parser.add_argument('--verbose', action='store_true', help='Run verbosely')
	parser.add_argument("-l","--log_level",dest="log_level",default="WARNING",help="set log level")    
	#parser.add_argument("--log-file",dest="log_level",default="WARNING",help="set log level")    

	subparsers = parser.add_subparsers(dest='subparser_name')

	parser_info = subparsers.add_parser('info')
	parser_info.set_defaults(func=_show_info)

	parser_start = subparsers.add_parser('start')
	parser_start.set_defaults(func=_start)

	parser_start = subparsers.add_parser('stop')
	parser_start.set_defaults(func=_stop)

	parser_open = subparsers.add_parser('open')
	parser_open.add_argument('path')
	parser_open.set_defaults(func=_open)

	parser_status = subparsers.add_parser('status')
	parser_status.set_defaults(func=_status)

	parser_pwd = subparsers.add_parser('pwd')
	parser_pwd.set_defaults(func=_pwd)

	parser_close = subparsers.add_parser('close')
	parser_close.set_defaults(func=_close)

	parser_save = subparsers.add_parser('save')
	parser_save.set_defaults(func=_save)

	parser_list = subparsers.add_parser('list')
	parser_list.add_argument('address_or_attach', choices = ['address', 'attach'], help = 'specify address or attach')
	parser_list.add_argument('index', nargs = '?', type=int, help="specify index of address")
	parser_list.set_defaults(func=_list)

	parser_checkout = subparsers.add_parser('import')
	parser_checkout.add_argument('vs_dir')
	parser_checkout.add_argument('surface_name')
	parser_checkout.set_defaults(func=_import)

	parser_checkout = subparsers.add_parser('commit')
	parser_checkout.add_argument('vs_dir')
	parser_checkout.add_argument('surface_name')
	parser_checkout.set_defaults(func=_commit)

	parser_checkout = subparsers.add_parser('checkout')
	parser_checkout.add_argument('surface_id')
	parser_checkout.add_argument('vs_dir')
	parser_checkout.set_defaults(func=_checkout)

	args = parser.parse_args()
	return args

def main():
	args = _parse_options()
	logging.basicConfig(level=args.log_level.upper(), format='%(asctime)s %(levelname)s:%(message)s')
	args.func(args)

if __name__ == '__main__':
	main()