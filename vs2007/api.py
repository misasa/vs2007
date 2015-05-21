import sys
import win32api
import win32con
import win32gui
import ctypes
import pywintypes
import psutil
import subprocess
import shlex
from optparse import OptionParser

g_uiGWM = 0
VS_GET_HWND = 100
VS_GET_HVSWND = win32con.WM_APP + 1
g_hVSWnd = 0
g_myhWnd = 0
g_r_message = ""
exe_path = 'VS2007.exe'

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [('dwData',ctypes.c_void_p),("cbData",ctypes.c_void_p),("lpData",ctypes.c_void_p)]

PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)

def on_terminate(proc):
    pass
    #print ("process {} terminated".format(proc))

def kill_vs(pid):
    print "stopping %s..." % exe_path
    proc = psutil.Process(pid)
    proc.terminate()
    gone, alive = psutil.wait_procs([proc], timeout = 5, callback=on_terminate)
    for p in alive:
        p.kill()

def start_vs():
    print "starting %s..." % exe_path
    command_line = "%s" % (exe_path)
    args = shlex.split(command_line)
    pp = subprocess.Popen(args)

def get_pid():
    for pid in psutil.get_pid_list():
        p = psutil.Process(pid)
        try:
            if p.name() == exe_path:
                return pid
        except psutil.AccessDenied:
            pass



def main():
    global VS_GET_HVSWND
    global g_hVSGWM
    global g_myhWnd
    global g_hVSWnd


    parser = OptionParser("usage: %prog [options] COMMAND")
    parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="make lots of noise")
#    parser.add_option("-i","--interactive",action="store_true",dest="interactive",default=True,help="interactive mode")
    parser.add_option("-t","--timeout",action="store",type="int",dest="timeout",default=0,help="specify timeout (ms)")
    parser.add_option("-d","--set_handle",action="store",type="int",dest="handle",default=0,help="specify window handle of VisualStage")
    parser.add_option("-g","--get_handle",action="store_true",dest="get_handle",default=False,help="get window handle of VisualStage")    
    parser.add_option("-i","--get_pid",action="store_true",dest="get_pid",default=False,help="get pid of VisualStage")    
    parser.add_option("-r","--start",action="store_true",dest="start_vs",default=False,help="start VisualStage")    
    parser.add_option("-k","--kill",action="store_true",dest="kill_vs",default=False,help="kill VisualStage")    

    (options, args) = parser.parse_args()

    timeout = options.timeout

    g_hVSWnd = options.handle

    pid = get_pid()
    if not pid == None:
        process = psutil.Process(pid)
        if options.kill_vs:
            kill_vs(pid)
            sys.exit()
        elif options.start_vs:
            print '%s is already running (PID: %d).' % (exe_path, pid)
            sys.exit()
    else:
        if options.start_vs:
            start_vs()
            sys.exit()
        elif options.kill_vs:
            print '%s is not running.' % exe_path
            sys.exit()            
        else:
            print 'Initialize Error!'
            sys.exit(1)

    if options.get_pid:
        print "SUCCESS %d" % pid
        sys.exit()

#    print vs2007_process.pid()

    
    # if len(args) > 1:
    #     parser.error("incorrect number of arguments")
    #get instance handle
    hInstance = win32api.GetModuleHandle()

    # the class name
    className = 'VS2007API'


    # create and initialize window class
    wndClass                = win32gui.WNDCLASS()
    wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
    wndClass.lpfnWndProc    = wndProc
    wndClass.hInstance      = hInstance
    wndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    wndClass.hCursor        = win32gui.LoadCursor(0, win32con.IDC_ARROW)
    wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
    wndClass.lpszClassName  = className

    # register window class
    wndClassAtom = None
    try:
        wndClassAtom = win32gui.RegisterClass(wndClass)
    except Exception, e:
        print e
        raise e

    hWindow = win32gui.CreateWindow(
        wndClassAtom,                   #it seems message dispatching only works with the atom, not the class name
        className,
        win32con.WS_MINIMIZE|win32con.WS_OVERLAPPED,        
#        win32con.WS_OVERLAPPEDWINDOW,
#        win32con.CW_USEDEFAULT,
#        win32con.CW_USEDEFAULT,
#        win32con.CW_USEDEFAULT,
#        win32con.CW_USEDEFAULT,
        100,100,400,100,
        0,
        0,
        hInstance,
        None)

    # Show & update the window
    #win32gui.ShowWindow(hWindow, win32con.SW_SHOWNORMAL)
    #win32gui.ShowWindow(hWindow, win32con.SW_SHOWMINIMIZED)
    #win32gui.UpdateWindow(hWindow)

    if hWindow:
        g_myhWnd = hWindow
    else:
        print 'Initialize Error!'
        sys.exit(1)
    GetUIGWM()

    if options.get_handle:
        GetVSHVSWND(timeout)
#        win32gui.SendMessageTimeout(hWindow, VS_GET_HVSWND, 0, 0, win32con.SMTO_ABORTIFHUNG, timeout)
        if g_hVSWnd != 0:
            print "SUCCESS %d" % g_hVSWnd
            sys.exit()
        else:
            print "FAILURE"
            sys.exit(1)


    if g_hVSWnd == 0:
        GetVSHVSWND(timeout)  
        #win32gui.SendMessageTimeout(hWindow, VS_GET_HVSWND, 0, 0, win32con.SMTO_ABORTIFHUNG, timeout)

    if g_hVSWnd:
#        if len(args) == 1:
        if not len(args) == 1:
            parser.error("incorrect number of arguments")

        command_lines = args[0].split(';')
        for command_line in command_lines:
            if command_line:
                send_command_and_receive_message(command_line, timeout)
#        else:
#
#         elif options.interactive:
# #            print "interactive"
#             Interactive("")
#         else:
# #            print "from stdin..."
#             Interactive("")
        sys.exit(0)
    else:
        print "Initialize Error!"
        sys.exit(1)
    #SendCommand("TEST_CMD\0")
        #win32gui.SendMessage(hWindow, win32con.WM_COMMAND,hWindow,0)
    
    #win32gui.PumpMessages()

def send_command_and_receive_message(command_line, timeout):
    try:
        r = SendCommand(command_line, timeout)
        if r:
            print g_r_message
        else:
            print "FAILURE"
    except pywintypes.error,e:
        error_code = e[0]
        error_in = e[1]
        error_msg = e[2]
        print "ERROR(%d) in %s: %s" % (e[0], e[1], e[2])            
    # if r:
    #     print g_r_message
    # else:
    #     print "FAILURE"
    sys.exit(1)

def Interactive(prompt):
    #global g_r_message
    if prompt != "":
        print "q for exit"
    while True:
        try:
            command_line=raw_input(prompt)
            if command_line == "q":
                return 0
            else:
                send_command_and_receive_message(command_line)
        except (EOFError):
            break
def SendCommand(command, timeout = 0):
    global g_hVSWnd
    global g_myhWnd

    CDS = COPYDATASTRUCT()
    CDS.dwData = 0
    CDS.cbData = len(command)
    bufr = ctypes.create_string_buffer(command)
    CDS.lpData = ctypes.addressof(bufr)
    ptr = ctypes.addressof(CDS)
    if timeout == 0:
        return win32gui.SendMessage(g_hVSWnd, win32con.WM_COPYDATA, g_myhWnd, ptr)
    else:
        return win32gui.SendMessageTimeout(g_hVSWnd, win32con.WM_COPYDATA, g_myhWnd, ptr, win32con.SMTO_ABORTIFHUNG, timeout)
    
def GetUIGWM():
    global g_uiGWM
    if g_uiGWM == 0:
        g_uiGWM = win32gui.RegisterWindowMessage("VS2007ControlAPI_GMSG_WM_VISUALSTAGE")


def GetVSHVSWND(timeout = 0):
    global g_uiGWM
    global g_hVSWnd
    global g_myhWnd
    global VS_GET_HWND
    
    if g_uiGWM and g_hVSWnd == 0:
        if timeout == 0:
            win32gui.SendMessage(win32con.HWND_BROADCAST, g_uiGWM, VS_GET_HWND, g_myhWnd)
        else:
            win32gui.SendMessageTimeout(win32con.HWND_BROADCAST, g_uiGWM, VS_GET_HWND, g_myhWnd, win32con.SMTO_ABORTIFHUNG, timeout)


def wndProc(hWnd, message, wParam, lParam):
    global g_uiGWM
    global VS_GET_HVSWND
    global VS_GET_HWND
    global g_hVSWnd
    global g_myhWnd
    global g_r_message

    if message == VS_GET_HVSWND:
        #print 'VS_GET_HVSWND'
        GetVSHVSWND()
        
        return 0
    elif message == win32con.WM_COMMAND:
        #print 'WM_COMMAND'
        #SendCommand("TEST_CMD\0")
        return 0
    
    elif message == win32con.WM_COPYDATA:
        #print 'WM_COPYDATA'
        pCDS = ctypes.cast(lParam, PCOPYDATASTRUCT)
        g_r_message = ctypes.string_at(pCDS.contents.lpData, pCDS.contents.cbData)
        return 0
    elif message == win32con.WM_DESTROY:
        #print 'Being destroyed'
        win32gui.PostQuitMessage(0)
        return 0

    elif message == g_uiGWM and wParam == VS_GET_HWND and lParam != hWnd:
        #print "g_hVSWnd: %d" % lParam
        g_hVSWnd = lParam
    else:
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)



if __name__ == '__main__':
    main()
