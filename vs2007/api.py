#!/usr/bin/env python
from optparse import OptionParser
import sys
try:
    import vs2007
    #from vs2007 import VS2007Process
except ImportError:
    pass

def _process():
    return vs2007.VS2007Process()

def _parser():
    parser = OptionParser("usage: %prog [options] COMMAND")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
    parser.add_option("-i","--interactive",action="store_true",dest="interactive",default=True,help="interactive mode")
    parser.add_option("-d","--set_handle",action="store",type="int",dest="handle",default=0,help="specify window handle of VisualStage")
    parser.add_option("-g","--get_handle",action="store_true",dest="get_handle",default=False,help="get window handle of VisualStage")    
    return parser

def _parse_options():
    parser = _parser()
    (options, args) = parser.parse_args()

    return options, args

def _get_handle():
    if vs2007.VS2007Process.is_running():
        handle = vs2007.VS2007Process.get_handle()
        return handle

def _set_handle(handle):
    if vs2007.VS2007Process.is_running():
        vs2007.VS2007Process.set_handle(handle)    

def _send_command(command):
    if vs2007.VS2007Process.is_running():
        vs2007p = vs2007.VS2007Process()
        return vs2007p.send_command(command)


def main():
    (options, args) = _parse_options()

    if options.handle:
        handle = options.handle
        _set_handle(handle)

    if options.get_handle:
        handle = _get_handle()
        if handle and handle != 0:
            print "SUCCESS %d" % handle
            sys.exit()
        else:
            print "FAILURE"
            sys.exit(1)

    if len(args) > 0:
        for command in args:
            print _send_command(command)

if __name__ == '__main__':
    main()
