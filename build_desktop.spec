# PyInstaller spec – UniShare Desktop (Windows/Mac/Linux)
import sys, os
from kivy_deps import sdl2, glew, angle
from kivymd import hooks_path as kivymd_hooks_path

ROOT = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

a = Analysis(
    [os.path.join(ROOT, 'main_kivy.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, 'assests'),     'assests'),
        (os.path.join(ROOT, 'data'),        'data'),
        (os.path.join(ROOT, 'kivy_views'),  'kivy_views'),
        (os.path.join(ROOT, 'controllers'), 'controllers'),
        (os.path.join(ROOT, 'models'),      'models'),
        (os.path.join(ROOT, 'utils'),       'utils'),
    ],
    hiddenimports=[
        'kivymd', 'kivy', 'PIL', 'requests',
        'controllers.auth_controller',
        'controllers.chat_controller',
        'controllers.feed_controller',
        'controllers.marketplace_controller',
        'controllers.profile_controller',
        'controllers.swipe_controller',
        'utils.firebase_client',
        'utils.api_client',
        'utils.data',
        'utils.network_server',
    ],
    hookspath=[kivymd_hooks_path],
    runtime_hooks=[],
    excludes=['PyQt5'],
    cipher=block_cipher,
    noarchive=False,
)

# Inclure toutes les DLLs Kivy (SDL2, GLEW, ANGLE)
for dep in sdl2.dep_bins + glew.dep_bins + angle.dep_bins:
    a.datas += Tree(dep, prefix='.')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(d, prefix='.') for d in sdl2.dep_bins + glew.dep_bins + angle.dep_bins],
    name='UniShare',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # Pas de fenêtre console
    icon=os.path.join(ROOT, 'assests', 'logo_unishare.png'),
    onefile=True,           # Un seul .exe autonome
)
