import sys
import os
from datetime import datetime


class Logger(object):
    def __init__(self, filename="run.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        # 1. 写入控制台 (如果有，比如在 IDE 中)
        if self.terminal:
            try:
                self.terminal.write(message)
                self.terminal.flush()
            except Exception:
                pass  # 防止某些特殊环境下控制台写入失败导致崩溃

        # 2. 写入文件
        try:
            self.log.write(message)
            self.log.flush()
        except Exception:
            pass

    def flush(self):
        if self.terminal:
            try:
                self.terminal.flush()
            except Exception:
                pass
        self.log.flush()


def setup_redirects(log_filename="run.log"):
    """
    初始化日志重定向：
    1. 确定日志路径（兼容 IDE 和 打包后的 EXE）
    2. 写入启动时间戳
    3. 接管 sys.stdout 和 sys.stderr
    """

    # 1. 确定保存路径
    if getattr(sys, 'frozen', False):
        # 打包环境：EXE 同级目录
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：以入口脚本 (main.py) 所在目录为准
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    log_path = os.path.join(base_dir, log_filename)

    # 2. 写入启动分割线
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 20} 启动时间: {datetime.now()} {'=' * 20}\n")
    except Exception as e:
        # 如果连文件都打不开（极少见，比如权限问题），打印一下但不阻断程序
        print(f"警告: 无法初始化日志文件: {e}")
        return

    # 3. 核心：接管标准输出
    # 实例化 Logger 并替换系统 stdout/stderr
    sys.stdout = Logger(log_path)
    sys.stderr = sys.stdout

    print(f"[Logger] 日志系统已启动，输出路径: {log_path}")