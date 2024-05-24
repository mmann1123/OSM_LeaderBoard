# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['dash_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['dash',
                'pandas',
                'geopandas',
                'requests',
                'pyyaml',
                'datetime',
                'dash_uploader', 
                'dash_table', 
                'shapely',
                'folium', 
                'matplotlib', 
                'mapclassify'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='leaderboard_win',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
