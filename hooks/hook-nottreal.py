
import os, sys, glob

DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        'nottreal',
        'controllers')

hiddenimports = ['src.nottreal.controllers.' + os.path.basename(f)[:-3]
                 for f in glob.glob(os.path.join(DIR, '*.py'))
                 if not f.endswith('__init__.py')]
                 
# from PyInstaller.utils.hooks import collect_submodules
#
# hiddenimports = collect_submodules('..src.nottreal.controllers')
#print(hiddenimports) 