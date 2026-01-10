import os
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from tkinter import messagebox

import requests
from packaging import version

from .config import APP_VERSION, config

REPO_OWNER = "StreLitziaYc"
REPO_NAME = "game_shadow_snap"


class UpdateManager:
    def __init__(self, root):
        self.root = root
        self.api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
        self.current_exe = sys.executable
        self.app_dir = os.path.dirname(self.current_exe)
        self.on_progress_change = None

        # 初始化时自动清理旧备份
        self._clean_old_backups()

    def _get_proxies(self):
        """
        【新增】根据配置生成代理字典
        如果 config 中 proxy_port 为空或 0，则返回 None
        """
        port = config.get("proxy_port", "")
        if port and str(port).strip():
            proxy_url = f"http://127.0.0.1:{port}"
            print(f"[Updater] 使用代理: {proxy_url}")
            return {
                "http": proxy_url,
                "https": proxy_url
            }
        return None

    def _request_with_fallback(self, url, stream=False, timeout=10):
        """
        尝试使用代理请求，如果代理连接失败，则自动回退到直连
        """
        proxies = self._get_proxies()

        try:
            # 1. 尝试使用配置的代理 (如果有)
            if proxies:
                print(f"[Updater] 尝试使用代理连接: {url}")
                return requests.get(url, headers={}, proxies=proxies, stream=stream, timeout=timeout)

            # 2. 如果没配置代理，直接直连
            else:
                print(f"[Updater] 代理连接不可用，尝试直连: {url}")
                return requests.get(url, headers={}, stream=stream, timeout=timeout)

        except (
                requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError) as e:
            # 3. 捕获代理相关的错误
            if proxies:
                print(f"[Updater] ⚠️ 代理连接失败 ({e})，正在尝试直连...")
                # 代理挂了，尝试去掉代理再请求一次 (Fallback)
                return requests.get(url, headers={}, proxies=None, stream=stream, timeout=timeout)
            else:
                # 如果本来就是直连出错，那就真没办法了，抛出异常
                raise e

    # 让外部（Tray）可以把更新函数传进来
    def set_progress_callback(self, callback):
        self.on_progress_change = callback

    def _clean_old_backups(self):
        """清理更新产生的备份文件 (.old)"""
        if getattr(sys, 'frozen', False):
            old_exe = self.current_exe + ".old"
            if os.path.exists(old_exe):
                try:
                    os.remove(old_exe)
                    print(f"[Updater] 已清理旧版本备份: {old_exe}")
                except Exception as e:
                    print(f"[Updater] 清理旧版本失败: {e}")

    def check_for_updates(self, silent=False):
        """检查更新主入口"""
        t = threading.Thread(target=self._do_check, args=(silent,), daemon=True)
        t.start()

    def _do_check(self, silent):
        print(f"[Updater] 正在检查更新 (当前版本: {APP_VERSION})")
        try:
            if APP_VERSION == "dev":
                print("[Updater] 当前为开发模式 (dev)，已跳过自动更新检查。")
                print("          (提示: 如需测试更新，请设置环境变量 GSS_VERSION=0.0.0)")
                return  # 直接结束，不发起任何网络请求！
            print(f"[Updater] 正在请求: {self.api_url}")
            response = self._request_with_fallback(self.api_url, timeout=10)
            if response.status_code != 200:
                # 尝试解析 GitHub 返回的详细错误 JSON
                try:
                    error_json = response.json()
                    # 提取 message 字段，例如 "API rate limit exceeded..."
                    error_msg = error_json.get("message", str(error_json))
                    documentation_url = error_json.get("documentation_url", "")
                except Exception:
                    # 如果返回的不是 JSON (比如网页报错)，直接读文本
                    error_msg = response.text[:200]  # 截取前200字防止太长
                    documentation_url = ""

                # 【核心】打印到控制台，这就是你要的调试信息！
                print(f"\n[Updater Error] 请求失败 (Code: {response.status_code})")
                print(f"[Updater Error] 原因: {error_msg}")
                if documentation_url:
                    print(f"[Updater Error] 文档: {documentation_url}\n")

                # 特殊处理 403 限流
                if response.status_code == 403:
                    if not silent:
                        # 在弹窗里也稍微提示一下
                        self._notify("检查受限", "GitHub API 请求频率过高，请稍后再试。")
                    return  # 结束方法，不抛出异常

                # 其他错误则抛出，进入下方的 except 流程
                raise Exception(f"HTTP {response.status_code}: {error_msg}")

            data = response.json()
            latest_tag = data.get("tag_name", "v0.0.0")

            # 查找 zip 下载链接
            download_url = ""
            for asset in data.get("assets", []):
                if asset["name"].endswith(".zip"):
                    download_url = asset["browser_download_url"]
                    break

            if not download_url:
                if not silent:
                    self._notify("检查失败", "未找到发布文件 (Asset)")
                return

            try:
                v_local = version.parse(APP_VERSION.lstrip("v"))
            except Exception:
                return  # 解析失败时跳过更新，防止开发环境损坏
            v_remote = version.parse(latest_tag.lstrip("v"))

            if v_remote > v_local:
                if silent:
                    # 静默模式：直接开始下载安装流程，下载完再弹窗确认重启
                    self._download_and_install(download_url, latest_tag)
                else:
                    # 手动模式：先询问
                    self.root.after(0, lambda: self._ask_to_update(download_url, latest_tag))
            else:
                if not silent:
                    self._notify("检查更新", f"当前已是最新版本 ({APP_VERSION})")

        except Exception as e:
            print(f"更新检查出错: {e}")
            if not silent: self._notify("检查失败", str(e))

    def _ask_to_update(self, url, version):
        print(f"[Updater] 发现新版本 {version}，正在下载...")
        if messagebox.askyesno("发现新版本", f"发现新版本 {version}！\n是否立即更新？"):
            t = threading.Thread(target=self._download_and_install, args=(url, version), daemon=True)
            t.start()

    def _download_and_install(self, url, version_tag):
        temp_zip = os.path.join(self.app_dir, "update_temp.zip")
        temp_new_exe = os.path.join(self.app_dir, "GameShadowSnap.new")

        try:
            # 1. 下载
            print(f"[Updater] 正在下载更新文件: {url}")
            r = self._request_with_fallback(url, stream=True, timeout=30)
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0

            # 用于计算网速的变量
            start_time = time.time()
            last_time = start_time
            last_downloaded_size = 0

            print(f"[Updater] 开始下载... 总大小: {total_size / 1024 / 1024:.2f} MB")

            with open(temp_zip, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 获取当前时间
                        current_time = time.time()
                        # 每隔 1 秒打印一次，避免刷屏太快看不清
                        if current_time - last_time >= 1.0:
                            # 计算这一秒内下载了多少字节
                            delta_bytes = downloaded_size - last_downloaded_size
                            delta_time = current_time - last_time

                            # 计算速度 (Bytes/s -> KB/s -> MB/s)
                            speed = delta_bytes / delta_time
                            speed_str = f"{speed / 1024:.2f} KB/s"
                            if speed > 1024 * 1024:
                                speed_str = f"{speed / 1024 / 1024:.2f} MB/s"

                            # 计算百分比
                            percent = 0
                            if total_size > 0:
                                percent = (downloaded_size / total_size) * 100
                            # 调用托盘更新回调
                            # 格式示例: "下载中: 45% (2.5 MB/s)"
                            status_text = f"正在更新: {percent:.1f}% ({speed_str})"
                            if self.on_progress_change:
                                self.on_progress_change(status_text)

                            # 打印进度 (使用 \r 可以让光标回到行首，实现单行刷新效果)
                            # 如果在某些 IDE 终端里 \r 无效，可以改成普通的 print(...)
                            print(
                                f"\r[下载中] 进度: {percent:.1f}% | 速度: {speed_str} | 已下载: {downloaded_size / 1024 / 1024:.2f} MB",
                                end="", flush=True)

                            # 更新变量，为下一秒做准备
                            last_time = current_time
                            last_downloaded_size = downloaded_size

            # 下载循环结束后，换个行，确保下一条日志不跟在进度条后面
            print("\n[Updater] 下载完成！")

            # 2. 解压 (只提取 exe，不覆盖用户的 config.json)
            with zipfile.ZipFile(temp_zip, 'r') as zf:
                exe_name = "GameShadowSnap.exe"
                if exe_name not in zf.namelist():
                    raise Exception("更新包中未找到 EXE 文件")

                with zf.open(exe_name) as source, open(temp_new_exe, "wb") as target:
                    shutil.copyfileobj(source, target)
            print(f"[Updater] 解压完成，正在准备替换...")

            # 3. 准备替换
            self.root.after(0, lambda: self._perform_replace_and_restart(temp_new_exe))

        except Exception as e:
            print(f"更新失败: {e}")
            self._notify("更新失败", f"下载或安装出错: {e}")
        finally:
            if os.path.exists(temp_zip):
                os.remove(temp_zip)

    def _perform_replace_and_restart(self, new_exe_path):
        # ================= 开发环境熔断保护 =================
        # 如果不是打包后的 EXE，绝对不能执行替换，否则会破坏 Python 环境
        if not getattr(sys, 'frozen', False):
            print(f"[Updater] 警告: 检测到开发环境！停止文件替换。")
            print(f"[Updater] 新文件已下载至: {new_exe_path}")
            messagebox.showinfo("开发模式保护",
                                "更新包下载成功！\n\n"
                                "但为了保护你的 Python 环境，开发模式下**不会执行**文件替换操作。\n"
                                "(因为 sys.executable 指向的是 python.exe)")
            return
        # ===========================================================
        # 执行文件替换并重启
        if self.on_progress_change:
            self.on_progress_change("正在安装新版本...")
        try:
            old_exe_backup = self.current_exe + ".old"

            if os.path.exists(old_exe_backup):
                os.remove(old_exe_backup)

            # 核心替换逻辑
            os.rename(self.current_exe, old_exe_backup)
            os.rename(new_exe_path, self.current_exe)

            # 【新增】替换完成，提示用户
            if self.on_progress_change:
                self.on_progress_change("更新就绪，等待重启")

            if messagebox.askyesno("更新完成", "新版本已安装，需要重启生效。\n是否立即重启？"):
                self._restart_program()
            else:
                # 如果用户点“否”，说明他想继续用旧版（内存中）
                # 此时应该把托盘状态清理干净，假装无事发生
                if self.on_progress_change:
                    self.on_progress_change(None)  # 传入 None 触发重置
                print("[Updater] 用户选择稍后重启。")

        except OSError as e:
            messagebox.showerror("更新失败", f"文件替换失败 (请尝试管理员运行): {e}")
            # 出错时也要重置托盘
            if self.on_progress_change:
                self.on_progress_change(None)
            # 尝试回滚
            if os.path.exists(old_exe_backup) and not os.path.exists(self.current_exe):
                os.rename(old_exe_backup, self.current_exe)

    def _restart_program(self):
        """重启自身"""
        subprocess.Popen([self.current_exe] + sys.argv[1:])
        self.root.quit()
        sys.exit()

    def _notify(self, title, msg):
        self.root.after(0, lambda: messagebox.showinfo(title, msg))
