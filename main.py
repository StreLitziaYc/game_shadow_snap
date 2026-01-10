
import threading
import queue
import tkinter as tk
import os

from src.logger import setup_redirects
from src.updater import UpdateManager
from src.utils import set_dpi_awareness, enforce_single_instance
from src.capture import CaptureManager
from src.ui.overlay import NotificationOverlay
from src.ui.tray import setup_tray


def main():
    # 0. 强制单实例 (最先执行)
    enforce_single_instance()

    # 1. 初始化系统设置
    set_dpi_awareness()

    # 2. 创建通信队列
    gui_queue = queue.Queue()

    # 3. 初始化模块
    # Tkinter root 必须在主线程创建
    root = tk.Tk()

    capture_mgr = CaptureManager(gui_queue)
    overlay_mgr = NotificationOverlay(root, gui_queue)
    # 初始化更新管理器 (会自动清理旧备份)
    update_mgr = UpdateManager(root)

    # 4. 启动子线程

    # 线程 A: 键盘监听
    t_kb = threading.Thread(target=capture_mgr.start_listener, daemon=True)
    t_kb.start()

    # 线程 B: 托盘图标
    # 定义退出回调，当托盘点击退出时，杀掉进程
    def on_exit():
        os._exit(0)

    t_tray = threading.Thread(target=setup_tray, args=(on_exit, update_mgr), daemon=True)
    t_tray.start()

    # 5. 启动时延迟2秒静默检查更新
    root.after(2000, lambda: update_mgr.check_for_updates(silent=True))

    # 6. 启动 GUI 循环 (主线程阻塞)
    overlay_mgr.process_queue()  # 开始轮询队列

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # 程序一启动就立刻接管日志
    # 放在任何其他业务逻辑之前，确保所有 import 过程中的报错也能被记录
    setup_redirects()
    main()
