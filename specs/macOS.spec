# -*- mode: python -*-

block_cipher = None


a = Analysis(['../nottreal.py'],
             pathex=[''],
             binaries=[],
             datas=[('../dist.nrc', 'dist.nrc'), ('../nottreal/controllers/', 'controllers/'), ('../nottreal/views/', 'views/'), ('../nottreal/resources/file.icns', '.'),],
             hiddenimports=['nottreal.controllers','nottreal.views','pkg_resources.py2_warn'],
             hookspath=['hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
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
		  icon='../nottreal/resources/appicon.icns',
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='nottreal')
app = BUNDLE(coll,
             name='NottReal.app',
             icon='../nottreal/resources/appicon.icns',
             bundle_identifier='uk.ac.nott.mrl.nottreal',
             info_plist={
                'CFBundleShortVersionString': 'v1.0.0',
                'NSHighResolutionCapable': True,
                'NSAppleScriptEnabled': False,
                'NSHumanReadableCopyright': 'Martin Porcheron and University of Nottingham',
                'CFBundleDocumentTypes': [{
                    'CFBundleTypeIconFile': 'file.icns',
                    'CFBundleTypeExtensions': ['nrc'],
                    'CFBundleTypeName': 'NottReal Configuration',
                    'CFBundleTypeRole': 'Viewer',
                    'LSHandlerRank': 'Owner',
                    'LSItemContentTypes': ['uk.ac.nott.mrl.nottreal.nrc'],
                    'LSIsAppleDefaultForType': True,
                    'NSDocumentClass': 'NR.Config'}],
                'UTExportedTypeDeclarations': [{
                    'LSTypeIsPackage': True,
                    'UTTypeConformsTo': ['com.apple.package','public.content'],
                    'UTTypeDescription': 'NottReal Configuration',
                    'UTTypeIconFile': 'file.icns',
                    'UTTypeIdentifier': 'uk.ac.nott.mrl.nottreal.nrc',
                    'UTTypeTagSpecification': {'public.filename-extension': 'nrc'}
                    }]
                })
