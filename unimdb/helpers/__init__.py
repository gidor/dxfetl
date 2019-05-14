import os
# import glob
# import logging

"""  helpers"""
import argparse
import os
import sys
import zipfile
from subprocess import check_output
import json
import csv

# from shutil import copyfile
import logging
import yaml
# import win32ui
# import win32con
# import win32gui
# from win32com.shell import shell, shellcon
import logging
from logging.config import dictConfig
import subprocess
import easygui
import json

logger = logging.getLogger()


def __get_json_cfg():
    try:
        with open(os.path.join(module_path(), "config.json")) as stream:
            try:
                return json.load(stream)
            except Exception as exc:
                print(exc)
                return None
    except Exception as exc:
        return None


def __get_yaml_cfg():
    try:
        with open(os.path.join(module_path(), "config.yaml")) as stream:
            try:
                return yaml.load(stream)
            except Exception as exc:
                print(exc)
                return None
    except Exception as exc:
        return None


def __getcfg():
    res = __get_json_cfg()
    if res is None:
        res = __get_yaml_cfg()
    if res is None:
        return {}
    return res


__config = None


def configure_logging(fname='cli'):
    """ configure logging """
    dictlogging = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                'datefmt': "%Y-%m-%d %H:%M:%S",
            },
            'brief': {
                'format': "%(message)s",
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'brief',
                'level': logging.INFO,
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'level': logging.DEBUG,
                'filename': module_relative_file('log', fname + '.log')[0],
                'maxBytes': 10485760,
                'backupCount': 300,
            },
        },
        'loggers': {
            '': {
                'handlers': ['file', 'console', ],
            },
            'CLI': {
                'handlers': ['file', 'console', ],
            },
        },
    }
    dictConfig(dictlogging)


def getcfg():
    global __config
    if __config is None:
        __config = __getcfg()
    return __config


def browseFolderDialog(msg='Selezione Cartella', start=None):
    if start is None:
        start = module_path()
    return easygui.diropenbox(msg=msg, title=None, default=start)


# def deprecato_browseFolderDialog(msg='Selezione Cartella', start=None):

#     if start is None:
#         start = module_path()
#     module_pidl = shell.SHGetFolderLocation(0, shellcon.CSIDL_PERSONAL, 0, 0)
#     # module_pidl = shell.SHParseDisplayName(start, 0, None)

#     pidl, display_name, image_list = shell.SHBrowseForFolder(
#         None,  # win32gui.GetDesktopWindow(),
#         module_pidl,  # module_pidl[0],
#         msg,
#         0,  # shellcon.backIF_BROWSEINCLUDEFILES,
#         None,
#         None
#     )

#     if (pidl, display_name, image_list) == (None, None, None):
#         path = None
#     else:
#         path = shell.SHGetPathFromIDList(pidl)
#     return path


def openFileDialog(extensions=None, multi=False, filename=None, msg=None):
    ret = easygui.fileopenbox(msg=msg, default=filename, filetypes=extensions, )
    return ret


"""
def deprecato_openFileDialog(extensions=None, multi=False, filename=None):
    # openFlags = win32con.OFN_OVERWRITEPROMPT | win32con.OFN_FILEMUSTEXIST
    openFlags = win32con.OFN_FILEMUSTEXIST
    if multi:
        openFlags |= win32con.OFN_ALLOWMULTISELECT

    dlg = win32ui.CreateFileDialog(1,
                                   None,
                                   filename,
                                   openFlags,
                                   extensions)
    #    extensionFilterString(extensions))

    if dlg.DoModal() != win32con.IDOK:
        return None

    return dlg.GetPathNames()

"""
# saveFileDialog
"""
def saveFileDialog(message=None, fileName=None):
    " Save file dialog. Returns path if one is entered. Otherwise it returns None. Availability: FontLab, Macintosh, PC "
    path = None
    openFlags = win32con.OFN_OVERWRITEPROMPT | win32con.OFN_EXPLORER
    mode_save = 1
    myDialog = win32ui.CreateFileDialog(mode_save, None, fileName, openFlags)
    myDialog.SetOFNTitle(message)
    is_OK = myDialog.DoModal()
    if is_OK == 1:
        path = myDialog.GetPathName()
    return path
"""


csv.field_size_limit(131072 * 2)


def create_dir(path):
    "create directory"
    if not os.path.exists(path):
        os.makedirs(path)


def testfile(fname):
    """
    test if prospective_dir is a directory or a zip and if is writabel
    """
    if os.path.isfile(fname):
        return fname
    else:
        raise argparse.ArgumentTypeError("{0} is not a file".format(fname))


def test_dir(prospective_dir, twrite=False, tzip=False):
    """
    test if prospective_dir is a directory or a zip and if is writabel
    """
    if tzip:
        if os.path.isfile(prospective_dir):
            if prospective_dir[-3:] == "zip":
                return prospective_dir
            else:
                raise argparse.ArgumentTypeError(
                    "{0} is not a zip nor path".format(prospective_dir))
    if not os.path.isdir(prospective_dir):
        raise argparse.ArgumentTypeError(
            "{0} is not a path".format(prospective_dir))
    if twrite:
        if os.access(prospective_dir, os.W_OK):
            return prospective_dir
        else:
            raise argparse.ArgumentTypeError(
                "no write permission  in {0}".format(prospective_dir))
    else:
        if os.access(prospective_dir, os.R_OK):
            return prospective_dir
        else:
            raise argparse.ArgumentTypeError(
                "no read permision in {0}".format(prospective_dir))


def readable_dirorzip(prospective_dir):
    "check params direcorty or zipfile"
    return test_dir(prospective_dir, twrite=False, tzip=True)


def readable_dir(prospective_dir):
    "check params is directory redable"
    return test_dir(prospective_dir, twrite=False, tzip=False)


def writable_dir(prospective_dir):
    "check params is directory writable"
    return test_dir(prospective_dir, twrite=True, tzip=False)


def we_are_frozen():
    """
    Returns whether we are frozen via py2exe.
    This will affect how we find out where we are located.
    """

    return hasattr(sys, "frozen")


def module_path():
    """ This will get us the program's directory,
    even if we are frozen using py2exe"""
    if we_are_frozen():
        return os.path.dirname(sys.executable)
        # return os.path.dirname(
        #     str(
        #         sys.executable,
        #         sys.getfilesystemencoding()))
    return os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)))
    # return str(
    #     os.path.dirname(
    #         os.path.dirname(
    #             os.path.dirname(__file__))),
    #     sys.getfilesystemencoding())


def module_relative(dirname):
    """ compute path relative to module base path """
    return os.path.join(module_path(), dirname)


def module_relative_file(dirname, fname):
    """ compute path relative to module base path """
    filepath = os.path.join(module_relative(dirname), fname)
    return filepath, os.path.isfile(filepath)


def zipdir(fname, path):
    """
        create a zip file conteining  the path
    """
    cwd = os.getcwd()
    os.chdir(os.path.dirname(path))
    try:
        zipf = zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED)
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for fileh in files:
                zipf.write(os.path.join(os.path.basename(root), fileh))
                # zipf.write(os.path.join(root, fileh))
        zipf.close()
    except Exception as ex:
        logging.error(ex)
    finally:
        os.chdir(cwd)


def write_json(dest, filename, data):
    """ write data to json"""
    fpath = os.path.join(dest, filename + ".json")
    fhan = open(fpath, "w")
    fhan.write(json.dumps(data))
    fhan.close()


def read_json(dest, filename):
    """ read  data from json"""
    fpath = os.path.join(dest, filename + ".json")
    if os.path.isfile(fpath):
        fhan = open(fpath, "r")
        data = json.loads(fhan.read())
        fhan.close()
        return data
    else:
        return {}


def execute_psql(
        path,
        files,
        hostname='localhost',
        port='5432',
        user='postgres',
        password='postgres',
        database='postgres'):
    """
    execute psql
        hostname the host to wich connect defaluts localhost
        port postgresql poert default 5432,
        user the dn user dfault postgres,
        password the user's password defaults postgres,
        database the database to wich connect defalts postggres,
        path the path from which execute,
        files the file to execute
    """
    cwd = os.getcwd()
    os.chdir(path)
    try:
        os.environ["PGPASSWORD"] = password
        cmdl = os.path.join(module_path(), "psql.exe") + \
            " -w -h " + hostname + " -p " + port + " -U " + user + \
            " -f " + files + " " + database
        logging.info(" execute " + cmdl)
        cmd_show_data = check_output(cmdl, shell=True)
        cmd_output = cmd_show_data.split('\r\n')
        for data in cmd_output:
            logging.info(data)
    except Exception as ex:
        logging.error(ex)
    finally:
        os.chdir(cwd)


def call(args):
    """
    execute generatesd posgresql script
    """
    if args.call:
        outdir = args.outdir[0]
        if args.database is None:
            logging.info("manca  database  impossibile eseguire")
            return
        else:
            database = args.database[0]
        if args.host is None:
            logging.info("manca host impossibile eseguire")
            return
        else:
            host = args.host[0]
        if args.password is None:
            logging.info("manca password impossibile eseguire")
            return
        else:
            password = args.password[0]
        if args.username is None:
            username = args.schemaname[0]
        else:
            username = args.username[0]
        if args.port is None:
            port = "5432"
        else:
            port = args.port[0]
        logging.info(" launching  executeme.sql")
        execute_psql(
            path=outdir,
            files="executeme.sql",
            hostname=host, port=port, user=username, password=password,
            database=database
        )


def unicode_csv_reader(unicode_csv_data, **kwargs):
    "wrapper for csv streamer wihc converts non utf8 characters"
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), **kwargs)
    for row in csv_reader:
            # decode UTF-8 back to Unicode, cell by cell:
        yield [str(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    "wrapper for csv streamer wihc converts non utf8 characters"
    for line in unicode_csv_data:
        # Convert from Windows-1252 to UTF-8
        yield line.replace('\0', '').decode('Windows-1252').encode('utf-8').replace("\\", "\\\\")
        # yield line.encode('utf-8')


def prm_read(fname):
    """ reads a catasto  parameter file """
    d = {}
    with open(fname) as f:
        for line in f:
            (key, val) = line.split(":")
            d[key.strip().replace(" ", "_")] = val.strip()
    return d

#############################################################
# Wrapper to comand
#############################################################


def pgsql2shp(filename='out', **kvargs):
    """parameter:
        filename *
        host
        port
        user
        password
        geoname
        database
        query
    """
    cfg = getcfg()
    args = []
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "pgsql2shp.exe")
    if not exists:
        msg = "Errore programma di utilita' pgsql2shp non trovato"
        logger.error(msg)
        raise Exception(msg)
    args.append(exe)
    # filename
    # val=kvargs.get("filename","out")
    if os.path.dirname(filename) == '':
        filename = module_relative_file('out', filename)
    args.append("-f")
    args.append(filename)
    # host
    val = kvargs.get("host", cfg["database"]["host"])
    args.append("-h")
    args.append(val)
    # port
    val = kvargs.get("port", cfg["database"]["port"])
    args.append("-p")
    args.append(str(val))
    # user
    val = kvargs.get("user", cfg["database"]["user"])
    args.append("-u")
    args.append(str(val))
    # geoname
    val = kvargs.get("geoname", "geom")
    if val is not None:
        args.append("-g")
        args.append(str(val))
    # password
    val = kvargs.get("password", cfg["database"]["password"])
    args.append("-P")
    args.append(str(val))
    # database
    val = kvargs.get("password", cfg["database"]["dbname"])
    args.append(str(val))
    # query
    val = kvargs.get("query", None)
    args.append(str(val))
    print(args)
    res = subprocess.call(args)
    return res


def ogr2ogr(indir='lavoro_FGN.gdb', outfile='out.sql', **kvargs):
    """parameter:
        geoname
        schema
        outfile
        indir
    """
    args = []
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "ogr2ogr.exe")
    if not exists:
        msg = "Errore programma di utilita' ogr2ogr non trovato"
        logger.error(msg)
        raise Exception(msg)

    args.append(exe)
    args.append("-skipfailures")
    args.append("-f")
    args.append("PGDUMP")

    # geoname
    val = kvargs.get("geoname", "geom")
    args.append("-lco")
    args.append("GEOMETRY_NAME=%s" % val)

    # schema
    val = kvargs.get("schema", "gaia")
    args.append("-lco")
    args.append("SCHEMA=%s" % val)

    args.append("-lco")
    args.append("SRID=0")
    args.append("-lco")
    args.append("FID=gid")
    args.append("-lco")
    args.append("SPATIAL_INDEX=OFF")

    # outfile
    # val=kvargs.get("outfile","out.sql")
    if os.path.dirname(outfile) == '':
        outfile, _ = module_relative_file('out', outfile)
    args.append(outfile)
    # indir
    # val=kvargs.get("indir","lavoro_FGN.gdb")
    args.append(indir)
    logger.debug(str(args))
    os.environ["GDAL_DATA"] = module_relative(os.path.join('bin', 'gdal-data'))
    res = subprocess.call(args)
    return res


def iconv(infile=None, outfile=None, **kvargs):
    """parameter:
        infile
        outfile
    """
    if infile is None or outfile is None:
        return
    args = []
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "iconv.exe")
    if not exists:
        msg = "Errore programma di utilita' iconv non trovato"
        logger.error(msg)
        raise Exception(msg)

    args.append(exe)
    # filename
    args.append("-s")
    args.append("-c")
    args.append("-f")
    args.append("CP1125")
    args.append("-t")
    args.append("UTF-8")
    # val=kvargs.get("infile", None)
    args.append(infile)
    # val=kvargs.get("outfile", None)
    val = outfile
    fh = open(val, "w")
    logger.debug(str(args))

    res = subprocess.call(args, stdout=fh)
    fh.close()
    return res


def psql(infile=None, **kvargs):
    """parameter:
        host
        port
        user
        password
        dbname
        infile
    """
    if infile is None:
        return
    args = []
    cfg = getcfg()
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "psql.exe")
    if not exists:
        msg = "Errore programma di utilita' plsql non trovato"
        logger.error(msg)
        raise Exception(msg)
    args.append(str(exe))
    # host
    val = kvargs.get("host", cfg["database"]["host"])
    args.append("-h")
    args.append(str(val))
    # port
    val = kvargs.get("port", cfg["database"]["port"])
    args.append("-p")
    args.append(str(val))
    # user
    val = kvargs.get("user", cfg["database"]["user"])
    args.append("-U")
    args.append(str(val))

    # infile
    # val=kvargs.get("infile", None )
    args.append("-f")
    args.append(infile)
    # dbname
    val = kvargs.get("dbname", cfg["database"]["dbname"])
    args.append(str(val))

    # password
    val = kvargs.get("password", cfg["database"]["password"])
    os.environ["PGPASSWORD"] = str(val)

    logger.debug(str(args))
    print(args)
    res = subprocess.call(args)
    return res


def pg_ctl(**kvargs):
    """parameter:
        host
        port
        user
        password
        dbname
        infile
    """
    args = []
    cfg = getcfg()
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "pg_ctl.exe")
    if not exists:
        msg = "Errore programma di utilita' pg_ctl non trovato"
        logger.error(msg)
        raise Exception(msg)
    args.append(str(exe))
    for name in kvargs:
        if name == '_':
            args.append(str(kvargs[name]))
        else:
            args.append("-" + name)
            if kvargs[name] is not None:
                args.append(str(kvargs[name]))

    logger.debug(str(args))
    res = subprocess.call(args)
    return res


def initdb(**kvargs):
    """parameter:
    """
    args = []
    cfg = getcfg()
    exe, exists = module_relative_file(
        os.path.join("pgsql", "bin"), "initdb.exe")
    if not exists:
        msg = "Errore programma di utilita' initdb non trovato"
        logger.error(msg)
        raise Exception(msg)
    args.append(str(exe))
    for name in kvargs:
        if name == '_':
            args.append(str(kvargs[name]))
        else:
            args.append("-" + name)
            if kvargs[name] is not None:
                args.append(str(kvargs[name]))

    logger.debug(str(args))
    res = subprocess.call(args)
    return res


APP_NAME = 'Etl'
DEFAULT_DIR = os.path.join(module_path(), 'out')
