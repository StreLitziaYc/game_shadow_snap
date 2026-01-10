import os
import pystray
from PIL import Image, ImageDraw
from ..config import config, get_resource_path, APP_VERSION


def create_default_icon():
    width = 64
    height = 64
    color1 = (0, 120, 215);
    color2 = (255, 255, 255)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color2)
    return image


def setup_tray(stop_callback, update_mgr):
    icon_path = get_resource_path('camera.ico')
    save_dir = config.get('save_dir')
    hotkey = config.get('hotkey')

    def open_folder(icon, item):
        os.startfile(os.path.abspath(save_dir))

    def check_update_action(icon, item):
        update_mgr.check_for_updates(silent=False)  # 手动检查

    def exit_program(icon, item):
        icon.stop()
        stop_callback()

    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        image = create_default_icon()

    # TODO: 未来在这里添加 "设置" 菜单
    menu = (
        pystray.MenuItem(f'GameShadowSnap {APP_VERSION}', lambda i, It: None, enabled=False),
        pystray.MenuItem(f'热键: {hotkey}', lambda i, It: None, enabled=False),
        pystray.MenuItem('打开保存文件夹', open_folder),
        pystray.MenuItem('检查更新', check_update_action),
        pystray.MenuItem('退出', exit_program)
    )

    icon = pystray.Icon("GameShadowSnap", image, "GameShadowSnap", menu)

    # 定义一个内部函数，用来更新图标的 Tooltip (悬停文字)
    def update_tray_tooltip(text):
        # 这里的 text 就是 Updater 传过来的 "正在更新: 45%..."
        # 我们把它拼接到软件名后面
        if icon:
            if text is None:
                # 传入 None 时，恢复干净的默认状态
                icon.title = f"GameShadowSnap"
            else:
                # 有内容时，显示状态
                icon.title = f"GameShadowSnap-{APP_VERSION}\n{text}"
    # 将这个函数注册给 UpdateManager
    # 这样当 updater 里的进度变化时，就会自动调用上面这个函数
    update_mgr.set_progress_callback(update_tray_tooltip)
    icon.run()
