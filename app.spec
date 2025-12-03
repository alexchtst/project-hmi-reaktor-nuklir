# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('asset', 'asset'),           # Include folder asset
        ('data', 'data'),             # Include folder data
        ('ui', 'ui'),                 # Include folder ui
        ('library', 'library'),       # Include folder library
        ('module', 'module'),         # Include folder module
        ('worker_connectandsetup.py', '.'),  # Include worker files
        ('worker_dynamic.py', '.'),
        ('worker_runloadflow.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyd = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyd,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AplikasiReaktorNuklir',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = tidak tampil console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='asset/logo-ugm.jpg'  # Tambahkan icon jika ada
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AplikasiReaktorNuklir'
)