import ctypes
import json
import os
import queue  # 引入队列库
import sys
import threading
import tkinter as tk
from datetime import datetime

import keyboard
import pystray
from PIL import Image, ImageGrab, ImageDraw

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
        print("配置文件不存在，正在创建默认配置...")
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"创建配置文件失败: {e}")
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            # 简单的合并逻辑：防止旧配置文件缺少新字段导致报错
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
# 获取是否拦截按键的配置
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


# ==================== 核心修复：常驻 GUI 引擎 ====================

# 创建一个全局的消息队列
msg_queue = queue.Queue()


class NotificationOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 初始状态：隐藏

        # 窗口属性设置
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)
        self.root.configure(bg="#333333")

        self.label = tk.Label(self.root, text="", bg="#333333", fg="#00FF00",
                              font=("微软雅黑", 12, "bold"), padx=15, pady=8)
        self.label.pack()

        self.hide_job = None  # 用于存储定时关闭的任务ID

        # 启动队列监听
        self.check_queue()
        self.root.mainloop()

    def check_queue(self):
        """每隔50ms检查一次队列"""
        try:
            # 尝试从队列获取消息，不阻塞
            while True:
                message = msg_queue.get_nowait()
                self.show_message(message)
        except queue.Empty:
            pass

        # 循环调用
        self.root.after(50, self.check_queue)

    def show_message(self, message):
        """显示窗口并更新文字"""
        self.label.config(text=message)

        # 计算位置（每次显示都重新计算，以跟随焦点屏幕）
        try:
            bbox = get_current_monitor_bbox()
            monitor_x = bbox[0]
            monitor_width = bbox[2] - bbox[0]
            center_x = monitor_x + (monitor_width // 2) - 50
            monitor_y = bbox[1] + 20
            self.root.geometry(f"+{center_x}+{monitor_y}")
        except:
            sw = self.root.winfo_screenwidth()
            self.root.geometry(f"+{int(sw / 2 - 50)}+20")

        # 显示窗口
        self.root.deiconify()

        # 如果之前有正在进行的“隐藏倒计时”，先取消它（防止连按时窗口闪烁关闭）
        if self.hide_job:
            self.root.after_cancel(self.hide_job)

        # 重新设定 2秒后隐藏
        self.hide_job = self.root.after(2000, self.hide_window)

    def hide_window(self):
        """隐藏窗口（而不是销毁）"""
        self.root.withdraw()
        self.hide_job = None


# 在独立线程中启动 GUI 引擎
def start_gui_thread():
    app = NotificationOverlay()


# ---------------- 截图功能模块 ----------------
def get_unique_filepath(directory, filename_base, extension):
    filename = f"{filename_base}{extension}"
    filepath = os.path.join(directory, filename)
    counter = 1
    while os.path.exists(filepath):
        filename = f"{filename_base}_{counter}{extension}"
        filepath = os.path.join(directory, filename)
        counter += 1
    return filepath, filename


def take_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_base = f"screenshot_{timestamp}"
        filepath, final_filename = get_unique_filepath(SAVE_DIR, filename_base, ".png")

        bbox = get_current_monitor_bbox()
        screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)

        screenshot.save(filepath)
        print(f"截图保存: {filepath}")

        # === 修复点：不再创建窗口，而是只发消息 ===
        if config.get('show_notification', True):
            msg_queue.put(f"保存成功\n{final_filename}")

    except Exception as e:
        print(f"截图失败: {e}")


# ---------------- 托盘控制模块 ----------------
def open_folder(icon, item):
    os.startfile(os.path.abspath(SAVE_DIR))


def exit_program(icon, item):
    icon.stop()
    os._exit(0)


def run_keyboard_listener():
    print(f"键盘监听已启动，热键: {HOTKEY}, 独占模式: {SUPPRESS_KEY}")
    try:
        keyboard.add_hotkey(HOTKEY, take_screenshot, suppress=SUPPRESS_KEY)
        keyboard.wait()
    except Exception as e:
        print(f"监听出错: {e}")


def main():
    # 1. 启动 GUI 线程 (消费者)
    # daemon=True 意味着主程序退出时，这个线程也会自动死掉
    threading.Thread(target=start_gui_thread, daemon=True).start()

    # 2. 启动键盘监听线程 (生产者)
    t = threading.Thread(target=run_keyboard_listener, daemon=True)
    t.start()

    # 3. 启动托盘 (主线程阻塞在这里)
    if os.path.exists(ICON_FILE):
        image = Image.open(ICON_FILE)
    else:
        image = create_default_icon()

    menu = (
        pystray.MenuItem(f'热键: {HOTKEY} ({"独占" if SUPPRESS_KEY else "共享"})', lambda i, It: None, enabled=False),
        pystray.MenuItem('打开保存文件夹', open_folder),
        pystray.MenuItem('退出', exit_program)
    )

    icon = pystray.Icon("ShadowSnap", image, "ShadowSnap 截图助手", menu)
    icon.run()


if __name__ == "__main__":
    main()
