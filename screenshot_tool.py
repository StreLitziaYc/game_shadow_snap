import keyboard
import time
import os
import sys
import json
import threading
import tkinter as tk
import ctypes
from ctypes import wintypes
from PIL import Image, ImageGrab, ImageDraw
import pystray
from datetime import datetime

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
    # === 新增 suppress_key 选项，默认为 True (拦截) ===
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
HOTKEY = config.get('hotkey', 'f9')
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


# ---------------- 无焦点提示框模块 ----------------
def show_toast_overlay(message="截图已保存"):
    def run_gui():
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.attributes("-alpha", 0.85)
            root.configure(bg="#333333")

            label = tk.Label(root, text=message, bg="#333333", fg="#00FF00",
                             font=("微软雅黑", 12, "bold"), padx=15, pady=8)
            label.pack()

            try:
                bbox = get_current_monitor_bbox()
                monitor_x = bbox[0]
                monitor_width = bbox[2] - bbox[0]
                center_x = monitor_x + (monitor_width // 2) - 50
                monitor_y = bbox[1] + 20
                root.geometry(f"+{center_x}+{monitor_y}")
            except:
                sw = root.winfo_screenwidth()
                root.geometry(f"+{int(sw / 2 - 50)}+20")

            root.after(2000, root.destroy)
            root.mainloop()
        except:
            pass

    threading.Thread(target=run_gui, daemon=True).start()


# ---------------- 截图功能模块 ----------------
def take_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(SAVE_DIR, filename)

        bbox = get_current_monitor_bbox()
        screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)

        screenshot.save(filepath)
        print(f"截图保存: {filepath}")

        if config.get('show_notification', True):
            show_toast_overlay(f"保存成功\n{filename}")
    except Exception as e:
        print(f"截图失败: {e}")


# ---------------- 托盘控制模块 ----------------
def open_folder(icon, item):
    os.startfile(os.path.abspath(SAVE_DIR))


def exit_program(icon, item):
    icon.stop()
    os._exit(0)


def run_keyboard_listener():
    # === 关键修改：使用 suppress 参数控制是否拦截 ===
    print(f"键盘监听已启动，热键: {HOTKEY}, 独占模式: {SUPPRESS_KEY}")
    try:
        # suppress=True 表示拦截，False 表示透传
        keyboard.add_hotkey(HOTKEY, take_screenshot, suppress=SUPPRESS_KEY)
        keyboard.wait()
    except ImportError:
        pass


def main():
    t = threading.Thread(target=run_keyboard_listener, daemon=True)
    t.start()

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