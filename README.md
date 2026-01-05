# 📸 ShadowSnap

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://www.microsoft.com/windows)

**ShadowSnap** 是一款专为游戏玩家设计的轻量级截图工具。
它运行在系统后台，能够实现**零干扰、不抢占焦点**的截图体验，完美支持全屏游戏模式。

**ShadowSnap** is a lightweight screenshot tool designed specifically for gamers.
It runs in the background, providing a **zero-interruption, non-focus-stealing** screenshot experience, perfect for exclusive fullscreen games.

---

## ✨ 特性 / Features

- **🛡️ 零干扰 (Non-Intrusive)**: 截图成功后，屏幕顶部会弹出半透明悬浮提示，**绝对不会**导致游戏最小化或失去鼠标焦点。
- **🎮 全屏支持 (Fullscreen Ready)**: 专为全屏游戏优化，解决传统截图工具弹窗导致跳出的问题。
- **⌨️ 全局热键 (Global Hotkey)**: 自定义快捷键（默认 F9），随时记录精彩瞬间。
- **📥 托盘管理 (System Tray)**: 最小化至右下角托盘，支持右键菜单快速打开截图文件夹。
- **⚙️ 高度可配 (Configurable)**: 通过 `config.json` 轻松修改热键和保存路径。

## 🚀 快速开始 / Quick Start

### 方式一：直接运行 (Download EXE)
如果你没有 Python 环境，请直接下载 Release 页面中的 `ShadowSnap.exe`。

1. 下载并解压。
2. **右键以管理员身份运行** `ShadowSnap.exe` (为了确保在游戏中能监听到按键)。
3. 按下 `F9` 截图。
4. 在右下角托盘图标处右键可退出或查看文件。

### 方式二：源码运行 (Run from Source)

```bash
# 1. 克隆仓库
git clone [https://github.com/YourUsername/ShadowSnap.git](https://github.com/YourUsername/ShadowSnap.git)
cd ShadowSnap

# 2. 安装依赖
pip install keyboard Pillow pystray

# 3. 运行 (需管理员权限终端)
python screenshot_tool.py

```

## ⚙️ 配置 / Configuration

程序首次运行会在同目录下生成 `config.json`，你可以修改它：

```json
{
    "hotkey": "f9", 
    "save_dir": "D:\\GameScreenshots",
    "show_notification": true
}

```

* `hotkey`: 触发按键 (例如: "f9", "ctrl+alt+a", "print screen")。
* `save_dir`: 图片保存文件夹路径 (请使用双反斜杠 `\\` 或正斜杠 `/`)。
* `show_notification`: 是否显示截图成功的悬浮提示 (`true` 或 `false`)。

## 🛠️ 构建指南 / Build Instructions

如果你想自己打包 exe 文件：

1. 安装 PyInstaller:
```bash
pip install pyinstaller

```


2. 运行打包命令:
```bash
pyinstaller -F -w --uac-admin --icon=camera.ico screenshot_tool.py

```


*(注: `--uac-admin` 参数用于请求管理员权限，这对于在游戏中监听按键至关重要)*

## ⚠️ 常见问题 / FAQ

**Q: 为什么运行没反应？** A: 程序默认静默启动到右下角托盘，请检查任务栏右下角是否有相机图标。

**Q: 为什么在游戏里按键没反应？** A: 请务必**以管理员身份运行**程序。部分带有反作弊系统的游戏可能会屏蔽底层键盘钩子。

**Q: 杀毒软件报毒？** A: 由于使用了全局键盘监听 (Keyboard Hook) 和 PyInstaller 打包，可能会被误报。请将程序加入白名单。本项目完全开源，您可以自行审查代码。

## 📄 许可证 / License

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 开源。

---

*Made with ❤️ for Gamers.*
