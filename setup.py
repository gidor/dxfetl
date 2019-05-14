import os
import sys
from distutils.core import setup
import py2exe
import glob
sys.path.append(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "unimdb"))


# data_files = ["cfg.json"]
data_files = []

# listdir = glob.glob("tmpl/**/*.*")
# listdir = glob.glob("tmpl/*")
# lslv0 = []
# for vdir in listdir:
#     if os.path.isdir(vdir):
#         lslv1 = []
#         lsls = glob.glob(vdir + "/*")
#         for lv1 in lsls:
#             if os.path.isfile(lv1):
#                 lslv1.append(lv1)
#         f2 = (vdir, lslv1)
#         data_files.append(f2)
#     else:
#         lslv0.append(vdir)
# f2 = ('tmpl', lslv0)
# data_files.append(f2)

# listdir = glob.glob("binrsc/*.*")
# f2 = ('.', listdir)
# data_files.append(f2)

print data_files

setup(
    console=[
        'unimdb/etl.py',
        'unimdb/monografie.py',
    ],
    data_files=data_files,
    options={
        "py2exe": {
            "packages": [ "os","csv","argparse","pyodbc","sqlparse","ezdxf"  ],
            "unbuffered": True,
            "optimize": 2}})
#, "excludes": ["email"]
