import ctypes
import os
import sys
import time
import subprocess


class SingleInstanceChecker:
    def __init__(self, app_name="Global\\GameShadowSnap_Mutex"):
        self.mutex_name = app_name
        self.mutex_handle = None
        self.kernel32 = ctypes.windll.kernel32
        self.last_error = 0

    def try_acquire(self):
        """尝试获取锁。返回 True 表示我是唯一实例。"""
        self.mutex_handle = self.kernel32.CreateMutexW(None, False, self.mutex_name)
        self.last_error = self.kernel32.GetLastError()
        # ERROR_ALREADY_EXISTS = 183
        if self.last_error == 183:
            return False
        return True

    def kill_old_instances(self):
        """强制清理旧进程"""
        my_pid = os.getpid()
        # 注意：这里必须和你打包后的 exe 名字完全一致
        target_name = "GameShadowSnap.exe"

        print(f"[Startup] 发现旧实例，正在执行清理... (排除当前PID: {my_pid})")
        try:
            # /F:强制 /FI:过滤器排除自己 /IM:镜像名
            cmd = f'taskkill /F /FI "PID ne {my_pid}" /IM {target_name}'
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.5)
        except Exception as e:
            print(f"[Startup] 清理旧进程失败: {e}")

    def release(self):
        """释放句柄"""
        if self.mutex_handle:
            self.kernel32.CloseHandle(self.mutex_handle)
            self.mutex_handle = None


# 全局变量引用
_global_checker = None


def enforce_single_instance():
    """
    [主入口] 强制单实例运行
    """
    if not getattr(sys, 'frozen', False):
        return

    global _global_checker
    _global_checker = SingleInstanceChecker()

    if not _global_checker.try_acquire():
        _global_checker.kill_old_instances()
        _global_checker.release()

        # 重新初始化并再次占坑
        _global_checker = SingleInstanceChecker()
        if _global_checker.try_acquire():
            print("[Startup] 旧实例已清理，当前进程已接管 Mutex")