import tkinter as tk
import queue
from ..utils import get_current_monitor_bbox


class NotificationOverlay:
    def __init__(self, root, gui_queue):
        self.root = root
        self.gui_queue = gui_queue
        self.current_toast = None
        self.root.withdraw()  # 隐藏主窗口

    def create_toast(self, message):
        """创建提示窗口"""
        try:
            window = tk.Toplevel(self.root)
            self.current_toast = window

            # 窗口样式 (TODO: 未来在这里进行 UI 美化)
            window.overrideredirect(True)
            window.attributes("-topmost", True)
            window.attributes("-alpha", 0.85)
            window.configure(bg="#333333")

            label = tk.Label(window, text=f"保存成功\n{message}", bg="#333333", fg="#00FF00",
                             font=("微软雅黑", 12, "bold"), padx=15, pady=8)
            label.pack()

            # 位置计算
            try:
                bbox = get_current_monitor_bbox()
                center_x = bbox[0] + (bbox[2] - bbox[0]) // 2 - 50
                monitor_y = bbox[1] + 20
                window.geometry(f"+{center_x}+{monitor_y}")
            except:
                sw = window.winfo_screenwidth()
                window.geometry(f"+{int(sw / 2 - 50)}+20")

            # 自动关闭
            window.after(2000, lambda: self.close_toast(window))

        except Exception as e:
            print(f"弹窗创建失败: {e}")

    def close_toast(self, window=None):
        target = window if window else self.current_toast
        if target:
            try:
                target.destroy()
            except:
                pass
            if target == self.current_toast:
                self.current_toast = None

    def process_queue(self):
        """轮询队列"""
        try:
            while True:
                msg = self.gui_queue.get_nowait()

                if msg == "CLEAR":
                    self.close_toast()
                elif isinstance(msg, str):
                    self.close_toast()  # 先关旧的
                    self.create_toast(msg)
        except queue.Empty:
            pass

        # 继续轮询
        self.root.after(50, self.process_queue)