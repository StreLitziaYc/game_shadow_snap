import ctypes
import json
import os
import queue
import sys
import threading
import time
import tkinter as tk
from datetime import datetime

import keyboard
import pystray
from PIL import Image, ImageGrab, ImageDraw

# ==================== 全局变量管理 ====================
# 1. 创建一个线程安全的队列，用于子线程给主线程发消息
gui_queue = queue.Queue()

# 2. 全局记录当前的弹窗窗口对象，只在主线程中访问和修改
current_toast = None

# ==================== 系统 API 与 DPI 设置 ====================
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
    return mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom


# ---------------- 资源路径处理 ----------------
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ---------------- 配置加载模块 ----------------
CONFIG_FILE = 'config.json'
ICON_FILE = get_resource_path('camera.ico')


def load_config():
    default_config = {
        "hotkey": "f12",
        "save_dir": "./screenshots",
        "show_notification": True,
        "suppress_key": True
    }
    if not os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except:
            pass
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            for key, value in default_config.items():
                if key not in user_config:
                    user_config[key] = value
            return user_config
    except Exception as e:
        print(f"配置文件读取错误: {e}，将使用默认配置。")
        return default_config


config = load_config()
SAVE_DIR = config.get('save_dir', './screenshots')
HOTKEY = config.get('hotkey', 'f12')
SUPPRESS_KEY = config.get('suppress_key', True)

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


# ---------------- 生成默认图标 ----------------
def create_default_icon():
    width = 64;
    height = 64
    color1 = (0, 120, 215);
    color2 = (255, 255, 255)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color2)
    return image


# ---------------- 文件名生成 ----------------
def get_unique_filepath(directory, filename_base, extension):
    filename = f"{filename_base}{extension}"
    filepath = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{filename_base}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        counter += 1
    return filepath, filename


# ---------------- 截图功能模块 (在子线程运行) ----------------
def take_screenshot():
    # 1. 【关键步骤】在截图前，发送信号要求清除现有弹窗
    if config.get('show_notification', True):
        gui_queue.put("CLEAR")
        # 2. 【关键步骤】等待 0.1 秒，给主线程处理信号和屏幕刷新的时间
        # 这能确保截图时屏幕上没有残留的弹窗
        time.sleep(0.1)

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_base = f"screenshot_{timestamp}"
        filepath, final_filename = get_unique_filepath(SAVE_DIR, filename_base, ".png")

        bbox = get_current_monitor_bbox()
        screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)

        screenshot.save(filepath)
        print(f"截图保存: {filepath}")

        # 3. 截图完成后，发送消息要求显示新的弹窗
        if config.get('show_notification', True):
            gui_queue.put(final_filename)

    except Exception as e:
        print(f"截图失败: {e}")


# ---------------- 键盘监听 (在子线程运行) ----------------
def run_keyboard_listener():
    print(f"键盘监听启动: {HOTKEY}, 独占: {SUPPRESS_KEY}")
    try:
        keyboard.add_hotkey(HOTKEY, take_screenshot, suppress=SUPPRESS_KEY)
        keyboard.wait()
    except Exception as e:
        print(f"监听出错: {e}")


# ---------------- 托盘功能 (在子线程运行) ----------------
def setup_tray():
    def open_folder(icon, item):
        os.startfile(os.path.abspath(SAVE_DIR))

    def exit_program(icon, item):
        icon.stop()
        os._exit(0)

    if os.path.exists(ICON_FILE):
        image = Image.open(ICON_FILE)
    else:
        image = create_default_icon()

    menu = (
        pystray.MenuItem(f'热键: {HOTKEY}', lambda i, It: None, enabled=False),
        pystray.MenuItem('打开保存文件夹', open_folder),
        pystray.MenuItem('退出', exit_program)
    )

    icon = pystray.Icon("ShadowSnap", image, "ShadowSnap", menu)
    icon.run()


# ---------------- GUI 消息处理循环 (只在主线程运行) ----------------
def process_gui_queue(root):
    """
    主线程每隔一段时间检查一次队列，处理 GUI 请求
    """
    global current_toast

    try:
        # 尝试以非阻塞方式从队列获取消息
        while True:
            msg = gui_queue.get_nowait()

            # --- 处理 "CLEAR" 信号 ---
            if msg == "CLEAR":
                if current_toast is not None:
                    try:
                        # 在主线程中安全地销毁窗口
                        current_toast.destroy()
                    except:
                        pass
                    current_toast = None

            # --- 处理显示弹窗请求 (msg 是文件名字符串) ---
            elif isinstance(msg, str):
                # 为了保险，显示新窗口前也先销毁旧的
                if current_toast is not None:
                    try:
                        current_toast.destroy()
                    except:
                        pass
                    current_toast = None

                try:
                    # 创建依附于根窗口的子窗口 (Toplevel)
                    window = tk.Toplevel(root)
                    current_toast = window  # 更新全局引用

                    window.overrideredirect(True)
                    window.attributes("-topmost", True)
                    window.attributes("-alpha", 0.85)
                    window.configure(bg="#333333")

                    label = tk.Label(window, text=f"保存成功\n{msg}", bg="#333333", fg="#00FF00",
                                     font=("微软雅黑", 12, "bold"), padx=15, pady=8)
                    label.pack()

                    # 计算位置
                    try:
                        bbox = get_current_monitor_bbox()
                        monitor_x = bbox[0]
                        center_x = monitor_x + (bbox[2] - bbox[0]) // 2 - 50
                        monitor_y = bbox[1] + 20
                        window.geometry(f"+{center_x}+{monitor_y}")
                    except:
                        sw = window.winfo_screenwidth()
                        window.geometry(f"+{int(sw / 2 - 50)}+20")

                    # 2秒后自动关闭 (使用线程安全的 after 方法)
                    def auto_close(w):
                        try:
                            if w == current_toast:  # 确保只关闭自己
                                w.destroy()
                        except:
                            pass

                    window.after(2000, lambda w=window: auto_close(w))

                except Exception as e:
                    print(f"弹窗创建失败: {e}")

    except queue.Empty:
        # 队列为空，什么都不做
        pass

    # 安排自己 50 毫秒后再次运行，形成轮询循环
    root.after(50, lambda: process_gui_queue(root))


# ---------------- 主程序入口 ----------------
def main():
    # 1. 启动键盘监听线程 (Thread A)
    t_kb = threading.Thread(target=run_keyboard_listener, daemon=True)
    t_kb.start()

    # 2. 启动托盘图标线程 (Thread B)
    t_tray = threading.Thread(target=setup_tray, daemon=True)
    t_tray.start()

    # 3. 主线程负责 Tkinter GUI (Main Thread)
    # 创建一个隐藏的根窗口，它将一直存在
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 启动 GUI 消息处理循环
    process_gui_queue(root)

    # 进入 Tkinter 主事件循环，阻塞主线程
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
