import ctypes
import win32con
import win32api
import win32gui
import pywintypes
import sys
import logging

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [('dwData',ctypes.c_void_p),("cbData",ctypes.c_void_p),("lpData",ctypes.c_void_p)]

PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)

class VS2007API(object):
	g_uiGWM = None
	VS_GET_HWND = 100
	VS_GET_HVSWND = win32con.WM_APP + 1
	g_hVSWnd = None
	g_myhWnd = None
	g_r_message = ""

	@staticmethod
	def wndProc(hWnd, message, wParam, lParam):
		logging.info('wndProc %d %d %d %d' % (hWnd, message, wParam, lParam))

		if message == VS2007API.VS_GET_HVSWND:
			logging.info('VS2007API.VS_GET_HVSWND')
			VS2007API.GetVSHVSWND()
			return 0
		elif message == win32con.WM_COMMAND:
			logging.info('win32con.WM_COMMAND')
			return 0

		elif message == win32con.WM_COPYDATA:
			logging.info('win32con.WM_COPYDATA')
			pCDS = ctypes.cast(lParam, PCOPYDATASTRUCT)
			VS2007API.g_r_message = ctypes.string_at(pCDS.contents.lpData, pCDS.contents.cbData).decode('utf-8')
			return 0
		elif message == win32con.WM_DESTROY:
			logging.info('win32con.WM_DESTROY')
			win32gui.PostQuitMessage(0)
			return 0
		elif message == VS2007API.g_uiGWM and wParam == VS2007API.VS_GET_HWND and lParam != hWnd:
			logging.info('VS2007API.g_uiGWM')
			logging.info('receive g_hVSWnd %d' % lParam)
			VS2007API.g_hVSWnd = lParam
		else:
			logging.info('ELSE %d' % message)
			return win32gui.DefWindowProc(hWnd, message, wParam, lParam)


	@classmethod
	def GetUIGWM(cls):
		cls.g_uiGWM = win32gui.RegisterWindowMessage("VS2007ControlAPI_GMSG_WM_VISUALSTAGE")

	@classmethod
	def set_handle(cls, handle):
		logging.info('VS2007API.set_handle %d' % handle)
		cls.g_hVSWnd = handle

	@classmethod
	def get_handle(cls):
		return cls.g_hVSWnd

	@classmethod
	def GetVSHVSWND(cls, timeout):
		logging.info('SendMessage %d %d %d %d' % (win32con.HWND_BROADCAST, cls.g_uiGWM, cls.VS_GET_HWND, cls.g_myhWnd))
		win32gui.SendMessage(win32con.HWND_BROADCAST, cls.g_uiGWM, cls.VS_GET_HWND, cls.g_myhWnd)

	@classmethod
	def create_window(cls):
		# create and initialize window class
		hInstance = win32api.GetModuleHandle()
		className = 'VS2007API'
		wndClass                = win32gui.WNDCLASS()
		wndClass.style          = win32con.CS_HREDRAW | win32con.CS_VREDRAW
		wndClass.lpfnWndProc    = cls.wndProc
		wndClass.hInstance		= hInstance
		wndClass.hIcon          = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
		wndClass.hCursor        = win32gui.LoadCursor(0, win32con.IDC_ARROW)
		wndClass.hbrBackground  = win32gui.GetStockObject(win32con.WHITE_BRUSH)
		wndClass.lpszClassName  = className
		# register window class
		wndClassAtom = None
		try:
			wndClassAtom = win32gui.RegisterClass(wndClass)
		except Exception as e:
			logging.error(e)
			raise e

		hWindow = win32gui.CreateWindow(
			wndClassAtom,
			className,
			win32con.WS_MINIMIZE|win32con.WS_OVERLAPPED,
			100,100,400,100,0,0,
			hInstance,
			None
			)

		if hWindow:
			logging.info('g_myhWnd %d' % hWindow)
			cls.g_myhWnd = hWindow
		else:
			logging.critical('Initialize Error!')
			sys.exit(1)


	def __init__(self, hVSWnd = None):
		logging.info('VS2007API.__init__')
		self.logger = logging.getLogger(__name__)
		timeout = 0
		if self.g_myhWnd == None:
			self.create_window()
			
		if self.g_uiGWM == None:
			self.GetUIGWM()

		if hVSWnd:
			self.g_hVSWnd = hVSWnd

		if self.g_hVSWnd == None:
			logging.info('g_hVSWnd is None')
			self.GetVSHVSWND(timeout)
		else:
			logging.info('g_hVSWnd is not None')


	def send_command_and_receive_message(self, command_line, timeout = 0):
		try:
			r = self.SendCommand(command_line, timeout)
			if r:
				return self.g_r_message
			else:
				return "FAILURE"
#		except:
#			print(sys.exc_info())
		except pywintypes.error as e:
			error_code = e[0]
			error_in = e[1]
			error_msg = e[2]
			print("ERROR(%d) in %s: %s" % (e[0], e[1], e[2]))

	def SendCommand(self, command, timeout):
		b_command = command.encode('UTF-8')
		logging.info('SendCommand %s %d' % (b_command, timeout))
		CDS = COPYDATASTRUCT()
		CDS.dwData = 0
		CDS.cbData = len(b_command)
		bufr = ctypes.create_string_buffer(b_command)
		CDS.lpData = ctypes.addressof(bufr)
		ptr = ctypes.addressof(CDS)
		logging.info('SendMessage %d %d %d %d' % (self.g_hVSWnd, win32con.WM_COPYDATA, self.g_myhWnd, ptr))
		return win32gui.SendMessage(self.g_hVSWnd, win32con.WM_COPYDATA, self.g_myhWnd, ptr)
