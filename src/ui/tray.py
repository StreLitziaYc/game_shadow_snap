import os
import pystray
from PIL import Image, ImageDraw
from ..config import config, get_resource_path


def create_default_icon():
    width = 64;
    height = 64
    color1 = (0, 120, 215);
    color2 = (255, 255, 255)
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 4, height // 4, width * 3 // 4, height * 3 // 4), fill=color2)
    return image


def setup_tray(stop_callback):
    icon_path = get_resource_path('camera.ico')
    save_dir = config.get('save_dir')
    hotkey = config.get('hotkey')

    def open_folder(icon, item):
        os.startfile(os.path.abspath(save_dir))

    def exit_program(icon, item):
        icon.stop()
        stop_callback()

    if os.path.exists(icon_path):
        image = Image.open(icon_path)
    else:
        image = create_default_icon()

    # TODO: 未来在这里添加 "设置" 菜单
    menu = (
        pystray.MenuItem(f'热键: {hotkey}', lambda i, It: None, enabled=False),
        pystray.MenuItem('打开保存文件夹', open_folder),
        pystray.MenuItem('退出', exit_program)
    )

    icon = pystray.Icon("GameShadowSnap", image, "GameShadowSnap", menu)
    icon.run()