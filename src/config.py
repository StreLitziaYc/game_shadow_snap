import json
import os
import sys

# 优先读取系统环境变量 'GSS_VERSION' (方便IDE调试)
# 如果没有，默认为 'dev' (本地开发模式)
# CI 打包时，GitHub Actions 会把这一行替换为具体 Tag
APP_VERSION = os.getenv("GSS_VERSION", "dev")
# 确定配置文件的绝对路径，确保读写的是同一个文件
if getattr(sys, 'frozen', False):
    # 打包环境：使用 EXE 所在的目录
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境：使用入口脚本 (main.py) 所在的目录
    # sys.argv[0] 通常是 main.py 的路径
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')


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
            "suppress_key": True,
            "auto_update": True,
            "proxy_port": ""
        }
        self.data = self.load()

    def load(self):
        # 1. 如果文件不存在，直接写入默认配置
        if not os.path.exists(CONFIG_FILE):
            self.save(self.default_config)
            return self.default_config

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            print(f"[Config] 配置文件已加载: {user_config}")

            # 2. 【核心逻辑】检查并补全字段
            config_modified = False
            for key, default_value in self.default_config.items():
                if key not in user_config:
                    # 发现缺少字段，补进去
                    user_config[key] = default_value
                    config_modified = True
                    print(f"[Config] 检测到缺失字段 '{key}'，已自动补全。")

            # 3. 如果有修改，立刻写回文件，这样用户打开 json 就能看到新字段了
            if config_modified:
                self.save(user_config)

            return user_config

        except Exception as e:
            print(f"配置读取失败: {e}，将使用默认配置。")
            return self.default_config

    def save(self, data):
        """保存配置到文件"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"配置保存失败: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)


# 创建全局单例
config = ConfigManager()
