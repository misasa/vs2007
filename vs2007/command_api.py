#!/usr/bin/env python
from optparse import OptionParser
import sys
import logging
import vs2007
import vs2007.process

prog = "vs-api"
def _process():
    return vs2007.process.VS2007Process()

def _parser():
    parser = OptionParser("""usage: %prog [options] COMMAND

SYNOPSIS AND USAGE
  %prog [options] COMMAND

DESCRIPTION

EXAMPLE

SEE ALSO
  http://dream.misasa.okayama-u.ac.jp
  https://github.com/misasa/vs2007/blob/master/vs2007/command_api.py

IMPLEMENTATION
  Orochi, version 9
  Copyright (C) 2014-2020 Okayama University
  License GPLv3+: GNU GPL version 3 or later

HISTORY
  August 11, 2015: Add documentation
""")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
    parser.add_option("-i","--interactive",action="store_true",dest="interactive",default=False,help="interactive mode")
    parser.add_option("-d","--set_handle",action="store",type="int",dest="handle",default=0,help="specify window handle of VisualStage")
    parser.add_option("-g","--get_handle",action="store_true",dest="get_handle",default=False,help="get window handle of VisualStage")    
    parser.add_option("--set_pid",action="store",type="int",dest="pid",default=0,help="specify PID of VisualStage")
    parser.add_option("--get_pid",action="store_true",dest="get_pid",default=False,help="get PID of VisualStage")    
    parser.add_option("--timeout",action="store",type="int",dest="timeout", default=0,help="set timeout in msec (default: 0 msec)")
    parser.add_option("-l","--log_level",dest="log_level",default="WARNING",help="set log level")    
    return parser

def _parse_options():
    parser = _parser()
    (options, args) = parser.parse_args()

    return options, args

def _get_handle(timeout):
    logging.info('_get_handle')
    if vs2007.process.VS2007Process.is_running():
        handle = vs2007.process.VS2007Process.get_handle(timeout)
        return handle

def _set_handle(handle):
    logging.info('_set_handle')
    if vs2007.process.VS2007Process.is_running():
        vs2007.process.VS2007Process.set_handle(handle)    

def _get_pid():
    logging.info('_get_pid')
    if vs2007.process.VS2007Process.is_running():
        pid = vs2007.process.VS2007Process.get_pid()
        return pid

def _set_pid(pid):
    logging.info('_set_pid')
    vs2007.process.VS2007Process.set_pid(pid)    

def _send_command(command, timeout = 0):
    logging.info('_send_command')
    if vs2007.process.VS2007Process.is_running():
        vs2007p = vs2007.process.VS2007Process()
        return vs2007p.send_command(command, timeout)


def main():
    (options, args) = _parse_options()

    logging.basicConfig(level=options.log_level.upper(), format='%(asctime)s %(levelname)s:%(message)s')


    if options.pid:
        pid = options.pid
        _set_pid(pid)

    if options.get_pid:
        pid = _get_pid()
        if pid and pid != 0:
            print("SUCCESS %d" % pid)
            sys.exit()
        else:
            print("FAILURE")
            sys.exit(1)

    if options.handle:
        handle = options.handle
        _set_handle(handle)

    if options.get_handle:
        handle = _get_handle(options.timeout)
        if handle and handle != 0:
            print("SUCCESS %d" % handle)
            sys.exit()
        else:
            print("FAILURE")
            sys.exit(1)
    if options.interactive:
        while True:
            sys.stderr.write("vs-api>")
            #print("vs-api>", file=sys.stderr, end="")
            try:
                line = input()
                print(_send_command(line, options.timeout))
            except EOFError as e:
                break            

    if len(args) > 0:
        for command in args:
            print(_send_command(command, options.timeout))

if __name__ == '__main__':
    main()
