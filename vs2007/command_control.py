#!/usr/bin/env python
import vs2007
import vs2007.process as vs2007process
import argparse
from _version import __version__ as _version
_progname = 'vs'

def _process():
	p = vs2007process.VS2007Process()
	return p

def _start(args):
	vs2007.process.VS2007Process.start()

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
	if vs2007.process.VS2007Process.is_running():
		vs2007p = _process()
		pwd = vs2007p.pwd()
		print pwd

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
				print addr.to_s()
			elif args.address_or_attach == 'attach':
				for attach in addr.get_attachlist():
					print attach.to_s()

def _show_info(args):
	info = '%s %s' % (_progname, _version)
	if vs2007process.VS2007Process.is_running():
		info += ' with VisualStage %s' % _process()._get_version()
	_output(info)

def _output(text):
	print text


def _parse_options():
	parser = argparse.ArgumentParser(prog='vs')
	parser.add_argument('--verbose', action='store_true', help='Run verbosely')
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

	args = parser.parse_args()
	return args

def main():
	args = _parse_options()
	args.func(args)

if __name__ == '__main__':
	main()