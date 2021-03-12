import win32gui
import win32con
import win32api
import pywintypes
import ctypes
import time
import logging


class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
      ('dwData',ctypes.wintypes.LPARAM),
      ("cbData",ctypes.wintypes.DWORD),
      ("lpData",ctypes.c_char_p)
    ]
PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)
VS_MSG_ID = win32gui.RegisterWindowMessage("VS2007ControlAPI_GMSG_WM_VISUALSTAGE")
VS_GET_HWND = 100
logger = logging.getLogger(__name__)

class Window:
  className = "VS2007Messenger"
  wndClass = win32gui.WNDCLASS()
  wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
  wndClass.lpfnWndProc    = win32gui.DefWindowProc
  wndClass.hInstance		  = win32api.GetModuleHandle()
  wndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
  wndClass.hCursor        = win32gui.LoadCursor(0, win32con.IDC_ARROW)
  wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
  wndClass.lpszClassName  = className

  wndClassAtom = win32gui.RegisterClass(wndClass)
  @staticmethod
  def callback(e):
    logger.debug("original callback was called")
    logger.debug(e)

  def __init__(self):
    self.create_window()

  def create_window(self):
    hInstance = win32api.GetModuleHandle()
    handle = win32gui.CreateWindow(
      self.wndClassAtom,
      self.className,
      win32con.WS_MINIMIZE|win32con.WS_OVERLAPPED,
      100,100,400,100,0,0,
      hInstance,
      None
    )
    
    if handle:
      self.handle = handle
      self.hWnd = handle
    else:
      logging.critical('Initialize Error!')
  def close(self):
    logging.debug("closing window...")
    win32gui.PostMessage(self.handle,win32con.WM_CLOSE,0,0)

class VSHandler(Window):
  @staticmethod
  def wndProc(hWnd, message, wParam, lParam):
    logging.debug('wndProc VSHandler hWnd: %d message: %d wParam: %d lParam: %d' % (hWnd, message, wParam, lParam))

    if message == win32con.WM_COMMAND:
      logging.debug('win32con.WM_COMMAND')
      return 0
    elif message == win32con.WM_DESTROY:
      logging.debug('win32con.WM_DESTROY')
      win32gui.PostQuitMessage(0)
      return 0
    elif message == VS_MSG_ID and wParam == VS_GET_HWND and lParam != hWnd:
      logging.debug('message == VS_MSG_ID and wParam == VS_GET_HWD')
      logging.debug('receive g_hVSWnd %d' % lParam)
      VSHandler.callback(lParam)
    else:
      logging.debug('ELSE %d' % message)
      return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

  def __init__(self):
    super().__init__()

  def get_vs_handle(self, timeout = 0):
    logger.debug("get_vs_handle...")
    vs_handle = None
    def callback(e):
      nonlocal vs_handle
      logger.debug("callback called %d" % e)
      vs_handle = e
    self.__class__.callback = callback
    win32gui.SetWindowLong(self.handle, win32con.GWL_WNDPROC, self.wndProc)
    fuFlags = win32con.SMTO_ABORTIFHUNG
    logging.debug('SendMessageTimeout %d %d %d %d %d %d' % (win32con.HWND_BROADCAST, VS_MSG_ID, VS_GET_HWND, self.handle, fuFlags, timeout))
    try:
      send_at = time.time()
      r = win32gui.SendMessageTimeout(win32con.HWND_BROADCAST, VS_MSG_ID, VS_GET_HWND, self.handle, fuFlags, timeout)
      if r:
        logging.debug("response_time: %f sec" % (time.time() - send_at))
        logging.debug(r)
    except pywintypes.error as e:
      logging.error(e)
      logging.error("response_time: %f sec" % (time.time() - send_at))
    win32gui.SetWindowLong(self.handle, win32con.GWL_WNDPROC, win32gui.DefWindowProc)
    return vs_handle

class Messenger(Window):

  def __init__(self, vs_handle):
    super().__init__()
    self.vs_handle = vs_handle
    
    def callback(val):
      self.output = val

    def wndProc(hWnd, message, wParam, lParam):
      logging.debug('wndProc for Messenger hWnd: %d message: %d wParam: %d lParam: %d' % (hWnd, message, wParam, lParam))
      if message == win32con.WM_COMMAND:
          logging.debug('win32con.WM_COMMAND')
          return 0
      elif message == win32con.WM_COPYDATA:
        logging.debug('win32con.WM_COPYDATA')
        pCDS = ctypes.cast(lParam, PCOPYDATASTRUCT)
        r_message = ctypes.string_at(pCDS.contents.lpData, pCDS.contents.cbData).decode('utf-8')
        logging.debug("received: %s" % r_message)
        callback(r_message)
        return 0
      elif message == win32con.WM_DESTROY:
        logging.debug('win32con.WM_DESTROY')
        win32gui.PostQuitMessage(0)
        return 0
      else:
        logging.debug('ELSE %d' % message)
        return win32gui.DefWindowProc(hWnd, message, wParam, lParam)

    win32gui.SetWindowLong(self.handle, win32con.GWL_WNDPROC, wndProc)

  def command(self, command, timeout = 0):
    self.output = None
    self.SendCommand(command, timeout)
    return self.output

  def SendCommand(self, command, timeout = 0):
    b_command = command.encode('UTF-8')
    logging.debug('SendCommand %s %d' % (b_command, timeout))
    CDS = COPYDATASTRUCT()
    CDS.dwData = 0
    CDS.cbData = len(b_command)
    bufr = ctypes.create_string_buffer(b_command)
    CDS.lpData = ctypes.addressof(bufr)
    PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)
    ptr = PCOPYDATASTRUCT.from_address(ctypes.addressof(CDS))
    return win32gui.SendMessageTimeout(self.vs_handle, win32con.WM_COPYDATA, self.handle, ptr, win32con.SMTO_NORMAL, timeout)
