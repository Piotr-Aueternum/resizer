from distutils.core import setup
import py2exe, sys, os

sys.argv.append("py2exe")

setup(
    options={"py2exe": {"bundle_files": 1, "compressed": True}},
    windows=[{"script": "resize.py"}],
    zipfile=None,
)
exec "setup(console=[{'script': 'launcher.py', 'icon_resources': [(0, 'ICON.ico')],\
      'file_resources': [%s], 'other_resources': [(u'INDEX', 1, resource_string[:-1])]}],\
      options={'py2exe': py2exe_options},\
      zipfile = None )" % (bitmap_string[:-1])