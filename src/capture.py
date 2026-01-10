import time
import os
import keyboard
from datetime import datetime
from PIL import ImageGrab
from .config import config
from .utils import get_current_monitor_bbox, get_unique_filepath


class CaptureManager:
    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
        self.save_dir = config.get('save_dir')
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def take_screenshot(self):
        # 1. 清理 UI (防止画中画)
        if config.get('show_notification', True):
            self.gui_queue.put("CLEAR")
            time.sleep(0.1)

        try:
            # 2. 准备路径 (TODO: 未来在这里加入智能分类逻辑，修改 save_dir)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename_base = f"screenshot_{timestamp}"
            filepath, final_filename = get_unique_filepath(self.save_dir, filename_base, ".png")

            # 3. 截图
            bbox = get_current_monitor_bbox()
            screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)

            # 4. 保存
            screenshot.save(filepath)
            print(f"截图保存: {filepath}")

            # 5. TODO: 在这里添加【剪贴板复制】逻辑
            # 6. TODO: 在这里添加【音效播放】逻辑
            # 7. TODO: 在这里添加【手机快传】二维码生成逻辑

            # 8. 通知 UI
            if config.get('show_notification', True):
                self.gui_queue.put(final_filename)

        except Exception as e:
            print(f"截图失败: {e}")

    def start_listener(self):
        hotkey = config.get('hotkey')
        suppress = config.get('suppress_key')
        print(f"键盘监听启动: {hotkey}, 独占: {suppress}")
        try:
            keyboard.add_hotkey(hotkey, self.take_screenshot, suppress=suppress)
            keyboard.wait()
        except Exception as e:
            print(f"监听出错: {e}")