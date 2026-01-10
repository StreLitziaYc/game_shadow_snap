import ctypes
import os
from ctypes import wintypes


# 设置 DPI 感知
def set_dpi_awareness():
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


def get_unique_filepath(directory, filename_base, extension):
    """生成不重复的文件名"""
    filename = f"{filename_base}{extension}"
    filepath = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{filename_base}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        counter += 1
    return filepath, filename
