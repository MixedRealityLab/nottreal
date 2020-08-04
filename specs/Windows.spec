# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['../nottreal.py'],
             pathex=[''],
             binaries=[],
             datas=[('../dist.nrc', 'dist.nrc'), ('../nottreal/controllers/', 'controllers/'), ('../nottreal/views/', 'views/'), ('../nottreal/resources/appicon-128.ico', '.'),],
             hiddenimports=['nottreal.controllers','nottreal.views','pkg_resources.py2_warn'],
             hookspath=['hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='NottReal',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
		  icon='../nottreal/resources/appicon-128.ico',
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='nottreal')
