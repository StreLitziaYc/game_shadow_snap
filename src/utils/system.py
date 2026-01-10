import ctypes


def set_dpi_awareness():
    """设置 DPI 感知，防止界面模糊"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()


def get_current_monitor_bbox():
    """获取当前活动窗口所在显示器的坐标范围"""
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    hmonitor = user32.MonitorFromWindow(hwnd, 2)

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long),
                    ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_long), ('rcMonitor', RECT),
                    ('rcWork', RECT), ('dwFlags', ctypes.c_long)]

    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(hmonitor, ctypes.byref(mi))
    return (mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom)
