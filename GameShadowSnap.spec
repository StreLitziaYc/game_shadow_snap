# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

try:
    from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, MERGE
except ImportError:
    pass

# ================= 🛡️ 强制收集依赖区 =================
# 这里列出的库，PyInstaller 会把它们的所有文件（代码+二进制+数据）全部打包
# 彻底解决 requests 缺证书、Pillow 缺 _imaging、pystray 缺 dll 的问题
problematic_libs = ['certifi', 'requests', 'Pillow', 'pystray']

my_datas = [
    ('camera.ico', '.'),
    ('src', 'src'),
]
my_binaries = []
my_hiddenimports = []

for lib in problematic_libs:
    tmp_ret = collect_all(lib)
    my_datas += tmp_ret[0]
    my_binaries += tmp_ret[1]
    my_hiddenimports += tmp_ret[2]
# ===================================================

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=my_binaries,
    datas=my_datas,
    hiddenimports=my_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GameShadowSnap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='camera.ico',
    uac_admin=True,
)