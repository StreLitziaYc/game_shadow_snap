import json
import os
import sys

CONFIG_FILE = 'config.json'


# 获取资源路径（兼容 PyInstaller）
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ConfigManager:
    def __init__(self):
        self.default_config = {
            "hotkey": "f12",
            "save_dir": "./screenshots",
            "show_notification": True,
            "suppress_key": True
        }
        self.data = self.load()

    def load(self):
        if not os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.default_config, f, indent=4, ensure_ascii=False)
            except:
                pass
            return self.default_config

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并缺省配置
                for key, value in self.default_config.items():
                    if key not in user_config:
                        user_config[key] = value
                return user_config
        except Exception as e:
            print(f"配置读取失败: {e}")
            return self.default_config

    def get(self, key, default=None):
        return self.data.get(key, default)


# 创建全局单例
config = ConfigManager()
