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
        return os.path.dirname(
            unicode(
                sys.executable,
                sys.getfilesystemencoding()))
    return unicode(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__))),
        sys.getfilesystemencoding())


def module_relative(dirname):
    """ compute path relative to module base path """
    return os.path.join(module_path(), dirname)


def module_relative_file(dirname, fname):
    """ compute path relative to module base path """
    return os.path.join(module_relative(dirname), fname)


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


# def imm_convert(fromfile, tofile):
#     """
#      convert tiff image fromfile to tofile
#     """
#     try:
#         logging.info(fromfile + " " + tofile)
#         imm = Image.open(fromfile)
#         size = imm.size
#         imm.save(tofile)  # , "JPEG")
#         return size
#         # cmdl = os.path.join(module_path(), "convert.exe") + \
#         #     " " + fromfile + "  " + tofile
#         # cmd_show_data = check_output(cmdl, shell=True)
#     except Exception as ex:
#         logging.error(ex)
#         return (0, 0)


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
        yield [unicode(cell, 'utf-8') for cell in row]


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



APP_NAME = 'Etl'
DEFAULT_DIR = os.path.join(module_path(), 'out')

