# 📸 GameShadowSnap

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://www.microsoft.com/windows)

**GameShadowSnap** 是一款专为游戏玩家设计的轻量级截图工具。
它运行在系统后台，能够实现**零干扰、不抢占焦点**的截图体验，完美支持全屏游戏模式。

**GameShadowSnap** is a lightweight screenshot tool designed specifically for gamers.
It runs in the background, providing a **zero-interruption, non-focus-stealing** screenshot experience, perfect for exclusive fullscreen games.

---

## ✨ 特性 / Features

- **🛡️ 零干扰 (Non-Intrusive)**: 截图成功后，屏幕顶部会弹出半透明悬浮提示，**绝对不会**导致游戏最小化或失去鼠标焦点。
- **🎮 全屏支持 (Fullscreen Ready)**: 专为全屏游戏优化，解决传统截图工具弹窗导致跳出的问题。
- **⌨️ 全局热键 (Global Hotkey)**: 自定义快捷键（默认 F9），随时记录精彩瞬间。
- **📥 托盘管理 (System Tray)**: 最小化至右下角托盘，支持右键菜单快速打开截图文件夹。
- **⚙️ 高度可配 (Configurable)**: 通过 `config.json` 轻松修改热键和保存路径。

---

## 🚀 快速开始 / Quick Start

### 方式一：直接运行 (Download EXE)
如果你没有 Python 环境，请直接下载 Release 页面中的 `GameShadowSnap.zip`。

1. 下载并解压。
2. **右键以管理员身份运行** `GameShadowSnap.exe` (为了确保在游戏中能监听到按键)。
3. 按下 `F12` 截图。
4. 在右下角托盘图标处右键可退出或查看文件。

### 方式二：源码运行 (Run from Source)

```bash
# 1. 克隆仓库
git clone [https://github.com/StreLitziaYc/game_shadow_snap.git](https://github.com/StreLitziaYc/game_shadow_snap.git)
cd game_shadow_snap

# 2. 安装依赖
pip install keyboard Pillow pystray

# 3. 运行 (需管理员权限终端)
python main.py

```

## ⚙️ 配置 / Configuration

程序首次运行会在同目录下生成 `config.json`，你可以修改它：

```json
{
    "hotkey": "f12", 
    "save_dir": "./screenshots",
    "show_notification": true,
    "suppress_key": true
}

```

* `hotkey`: 触发按键 (例如: "f9", "ctrl+alt+a", "print screen")。
* `save_dir`: 图片保存文件夹路径 (请使用双反斜杠 `\\` 或正斜杠 `/`)。
* `show_notification`: 是否显示截图成功的悬浮提示 (`true` 或 `false`)。
* `suppress_key`: 是否屏蔽触发按键 (`true` 或 `false`)。

### ⌨️ 按键配置参考 / Key Configuration Reference

配置文件中的 `hotkey` 支持单键或组合键，组合键请使用 `+` 连接。不区分大小写。
The `hotkey` supports single keys or combinations joined by `+`. Case insensitive.

| 类型 / Type | 示例 / Examples |
| :--- | :--- |
| **功能键 (Function)** | `f1` ... `f12` |
| **修饰键 (Modifiers)** | `ctrl`, `alt`, `shift`, `win` (Windows徽标键) |
| **常用功能 (Common)** | `print screen`, `insert`, `home`, `page up`, `page down`, `delete`, `end` |
| **字母数字 (Typing)** | `a` ... `z`, `0` ... `9`, `space`, `tab`, `enter`, `backspace` |
| **小键盘 (Numpad)** | `num 0` ... `num 9`, `num lock`, `divide` (/), `multiply` (*), `subtract` (-), `add` (+) |

**组合键示例 / Combination Examples:**
* `"f12"`
* `"ctrl+f12"`
* `"alt+print screen"`
* `"ctrl+shift+a"`

> 🔗 **更多按键 / More Keys**:
> 如果需要查询非常规按键（如多媒体键），请查阅 [Python Keyboard 库官方文档](https://github.com/boppreh/keyboard#common-key-names)。
> For a complete list of supported key names, please refer to the official documentation.

---

## 🛠️ 构建指南 / Build Instructions

如果你想自己打包 exe 文件：

1. 安装 PyInstaller:
```bash
pip install pyinstaller

```


2. 运行打包命令:
```bash
pyinstaller -F -w --uac-admin --icon=camera.ico --add-data "camera.ico;." --add-data "src;src" -n "GameShadowSnap" main.py

```


*(注: `--uac-admin` 参数用于请求管理员权限，这对于在游戏中监听按键至关重要)*

---

## ⚠️ 常见问题 / FAQ

**Q: 为什么运行没反应？** A: 程序默认静默启动到右下角托盘，请检查任务栏右下角是否有相机图标。

**Q: 为什么在游戏里按键没反应？** A: 请务必**以管理员身份运行**程序。部分带有反作弊系统的游戏可能会屏蔽底层键盘钩子。

**Q: 杀毒软件报毒？** A: 由于使用了全局键盘监听 (Keyboard Hook) 和 PyInstaller 打包，可能会被误报。请将程序加入白名单。本项目完全开源，您可以自行审查代码。

---

## 🗺️ 路线规划 / Roadmap

我们欢迎社区贡献！如果你对以下任何功能感兴趣，欢迎提交 PR。
We welcome community contributions! If you are interested in any of the following features, feel free to submit a PR.

### 🎨 交互与体验 / UI & UX
- [ ] **UI 美化 (UI Polish)**: 优化提示框样式，支持圆角、渐变色、动画效果，甚至自定义皮肤。
  - *Enhance notification design with rounded corners, gradients, animations, or custom themes.*
- [ ] **配置界面 (GUI Settings)**: 开发一个可视化的设置窗口，不再依赖手动修改 `config.json`。
  - *Develop a visual settings window to replace manual `config.json` editing.*
- [ ] **音效反馈 (Sound Effect)**: 截图成功时播放清脆的快门声（可选开关）。
  - *Play a shutter sound upon successful screenshot (toggleable).*

### 🛠️ 核心功能增强 / Core Features
- [ ] **智能分类 (Smart Sorting)**: 自动识别当前游戏进程名，将截图保存到对应的子文件夹（例如 `Screenshots/Cyberpunk2077/`）。
  - *Auto-organize screenshots into subfolders based on the active game process name.*
- [ ] **剪贴板支持 (Copy to Clipboard)**: 截图后自动复制到剪贴板，方便直接粘贴到微信/Discord。
  - *Auto-copy to clipboard after screenshot for instant sharing.*
- [ ] **自定义文件名 (Custom Filename)**: 允许用户定义文件名格式（如 `{GameName}_{Date}.png`）。
  - *Allow users to define filename patterns.*
- [ ] **简易编辑器 (Simple Editor)**: 截图后提供简单的裁剪、涂鸦、打码功能。
  - *Provide simple cropping, drawing, and mosaic tools after capture.*
- [ ] **单实例检测 (Single Instance Check)**: 启动时自动检测是否已有 GameShadowSnap 在运行，若存在则询问用户是否重启，防止多开导致的热键冲突。
  - *Detect active instances on startup and prompt the user to restart to prevent hotkey conflicts caused by multiple processes.*

### 📡 连接与扩展 / Connectivity & Extensions
- [ ] **手机快传 (Mobile Transfer)**: 截图后生成二维码，手机扫码即可立即下载图片到本地。
  - *Generate a QR code to instantly download the latest screenshot to mobile devices via local network.*
- [ ] **自动更新 (Auto-Update)**: 启动时自动检测 GitHub Release 新版本并提示升级。
  - *Check for updates on startup and notify users of new versions available on GitHub.*
- [ ] **图床上传 (Cloud Upload)**: 支持自动上传到图床并生成分享链接。
  - *Auto-upload to cloud storage and generate shareable links.*

### 💻 工程化与重构 / Engineering & Refactoring
- [x] **代码模块化 (Modularization)**: 重构当前单文件代码，拆分为配置管理、GUI、系统监听等独立模块，提升可扩展性。
  - *Refactor the monolithic script into a modular architecture for better scalability and maintainability.*
- [x] **自动化构建 (CI/CD)**: 配置 GitHub Actions 实现自动打包 exe 并发布到 Releases，无需手动编译上传。
  - *Implement GitHub Actions for automated building and releasing artifacts.*

---

## 📄 许可证 / License

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 开源。

---

*Made with ❤️ for Gamers.*
