# -*- mode: python -*-

block_cipher = None


a = Analysis(['unimdb\\cli.py'],
             pathex=['C:\\DATA\\SVIL\\PYTHON\\uni\\unimdb'],
             binaries=[],
             datas=[('sql', 'sql'),
                    ('dxflib', 'dxflib'),
                    ('lsp', 'lsp'),
                    ('.dir', 'shp'),
                    ('tmpl', 'tmpl'),
                    ('bat', '.'),
                    ('config.yaml', '.'),
                    # ('logger.ini', '.'),
                    ('unimdb', 'src'),
                    ],
             hiddenimports=['cement',
                            'cement.ext.ext_dummy',
                            'cement.ext.ext_json',
                            'cement.ext.ext_tabulate',
                            'cement.ext.ext_smtp',
                            'cement.ext.ext_alarm',
                            'cement.ext.ext_argparse',
                            'cement.ext.ext_colorlog',
                            'cement.ext.ext_configparser',
                            'cement.ext.ext_daemon',
                            'cement.ext.ext_dummy',
                            'cement.ext.ext_generate',
                            'cement.ext.ext_jinja2',
                            'cement.ext.ext_json',
                            'cement.ext.ext_logging',
                            'cement.ext.ext_memcached',
                            'cement.ext.ext_mustache',
                            'cement.ext.ext_plugin',
                            'cement.ext.ext_print',
                            'cement.ext.ext_redis',
                            'cement.ext.ext_scrub',
                            'cement.ext.ext_smtp',
                            'cement.ext.ext_tabulate',
                            'cement.ext.ext_yaml',
                            'cement.ext.ext_watchdog',
                            ],
             hookspath=[],
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
          name='cli',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='cli')
