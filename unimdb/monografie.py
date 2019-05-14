"""
import sys
d=r"C:\local\svil\shpload\src"
d=r"C:\SVIL\Geocomp\acad_tools\IDROLARIO\MONOGRAFIE\src"
sys.path.append(d)
from mssql import ConnCreator
from sqlalchemy import create_engine
eng = create_engine('mssql://', creator= ConnCreator("CONCESSIONI\\SQLEXPRESS", "ProvForliCesena_Viabilita", "catstra", "catstra") )
import sqlalchemy as sa

tf=r"C:\SVIL\Geocomp\acad_tools\IDROLARIO\MONOGRAFIE\src\Scheda.html"

templ=pyratemp.Template(filename=tf,  data=d) ;

produzione dele schede di rilieavo per pozzetti
"""
import pyodbc
import os
import sys
import shutil
import jinja2
import subprocess
import imp
import argparse
import glob
import codecs
from helpers import we_are_frozen, testfile, module_relative_file, \
    module_relative, module_path, openFileDialog


class c (object):
    pass


"""    
    Day (s.data_rilievo) & "/" & Month(s.data_rilievo) & "/" & Year(s.data_rilievo) as data_rilievo,
    Format (s.data_rilievo, "dd/mm/yyyy") as data_rilievo,
"""

SQLScheda = """
SELECT 
    s.objectid as scheda_numero, 
    s.Comune , 
    Format([s].[data_rilievo], 'dd/mm/yyyy') as data_rilievo,
    s.data_rilievo as uuu,
    s.ubicazione,
    s.civico,
    s.note,
    s.id_pozzetto,
    s.punto,
    s.Condotta1,
    s.Condotta2,
    s.Condotta3,
    s.Condotta4,
    s.Condotta5,
    s.Condotta6,
    s.Condotta7,
    s.Condotta8,
    s.FotoEsterno  ,
    s.FotioInterno ,
    s.FotoComplessivo,
    s.FotoAltro,
    s.FotoEsterno1,
    s.FotioInterno1,
    s.FotoComplessivo1,
    s.FotoAltro1,     
    t.TIPFOG as tipologia
FROM 
    ((GEOMP_SCHEDA AS s INNER JOIN MASTER_P AS P ON s.punto = P.OBJ_ID )
      INNER JOIN TBLIDP AS id  on id.usedid = P.OBJ_ID )
      LEFT OUTER JOIN TIPFOG t on t.id=s.TIPO_FOGNATURA
"""
WhereSchedaALL = """ WHERE (((s.objectid)>0) AND ((P.CODE)=7)) OR (((P.CODE)=-1))"""
WhereSchedaBIANCA = """ WHERE (s.objectid>0) AND (s.tipo_fognatura = 2) AND ((P.CODE = 7) OR (P.CODE = -1)) """
# ~ WhereSchedaBIANCA =""" WHERE (((s.objectid)>0) AND (s.tipo_fognatura = 2) AND ((P.CODE)=7)) OR (((P.CODE)=-1))"""
# ~ WhereSchedaNERA =""" WHERE (((s.objectid)>0) AND ((s.tipo_fognatura = 3)  OR (s.tipo_fognatura = 4) ) AND ((P.CODE)=7)) OR (((P.CODE)=-1))"""
WhereSchedaNERA = """ WHERE (s.objectid>0) AND ((s.tipo_fognatura = 3)  OR (s.tipo_fognatura = 4) ) AND ((P.CODE = 7) OR (P.CODE = -1))"""
WhereSchedaSCHEDA = """ WHERE s.objectid=%s"""

"""
Round(( [P].[LARG_LIN] * 10),2) AS LARGHEZZA,
  Round(( [P].[ALT_LIN]  * 10),2) AS ALTEZZA,
  Round( [P].[PENDENZA] ,2) AS RPENDENZA,
  
"""


SQLPozzetto = """
SELECT 
  FCHIU.FORM as FORMA_CHIU, 
  P.LARG_CHIU, 
  P.LUNG_CHIU, 
  MCHIU.MAT as MAT_CHIU, 
  P.CARI_CHIU, 
  P.COP_CHIU, 
  P.APP_CHIU, 
  P.FORMA_SUP, 
  P.LARG_SUP, 
  P.LUNG_SUP, 
  MSUP.MAT AS MAT_SUP, 
  P.COLPOZ, 
  P.MAT_COLPOZ, 
  P.TRAVASO, 
  P.QUOTRAVASO, 
  P.FORMA_INF, 
  P.LARG_INF, 
  P.LUNG_INF, 
  MINF.MAT as MAT_INF, 
  P.QUOINFPOZ, 
  P.TOLINFPOZ, 
  P.TIPROGPOZ, 
  P.FORROGPOZ, 
  P.MATROGPOZ, 
  P.TIPPROROG, 
  P.TIPPROPOZ, 
  P.DIMPROPOZ
FROM (
      ((POZZETTO P LEFT OUTER JOIN MAT MCHIU ON MCHIU.ID=P.MAT_CHIU )
      LEFT OUTER JOIN MAT MINF  ON MINF.ID=P.MAT_INF)
    LEFT OUTER JOIN MAT MSUP  ON MSUP.ID=P.MAT_SUP)
  LEFT OUTER JOIN FORM FCHIU ON FCHIU.ID=P.FORMA_CHIU
where P.OBJ_ID =%d 
"""
SQLPunto = """
SELECT 
  TPS.TPS,
  P.*
FROM MASTER_P P
  LEFT OUTER JOIN TPS ON TPS.ID =P.CODE
where P.OBJ_ID =%d 
"""
SQLTratte = """
SELECT DISTINCT
  P.*,
  Switch(
  P.OBJ_ID =%(Condotta1)d , 1,
  P.OBJ_ID =%(Condotta2)d , 2,
  P.OBJ_ID =%(Condotta3)d , 3,
  P.OBJ_ID =%(Condotta4)d , 4,
  P.OBJ_ID =%(Condotta5)d , 5,
  P.OBJ_ID =%(Condotta6)d , 6,
  P.OBJ_ID =%(Condotta7)d , 7,
  P.OBJ_ID =%(Condotta8)d , 8,
  1,-1
  ) as IDSCHEDA,
  Switch(
  P.IDPUNINI=%(punto)d , 0,
  P.IDPUNFIN=%(punto)d , 1,
  1,-1 
  ) as INIFIN,
  t.TIPFOG as TIPOFOGNA,
  P.IDPUNINI,
  P.IDPUNFIN,
  P.DISLINI,
  P.DISLFIN,
  P.QUOINI,
  P.QUOFIN,
  P.LARG_LIN * 10 AS LARGHEZZA,
  P.ALT_LIN  * 10 AS ALTEZZA,  
  F.FORSEZ AS FORMA,
  M.MAT AS MATERIALE
FROM (((
  MASTER_L P INNER JOIN TBLID AS id  on id.usedid = P.OBJ_ID )
    LEFT OUTER JOIN TIPFOG T ON T.ID=P.TIPFOG)  
    LEFT OUTER JOIN FORSEZ F ON F.ID=P.FORSEZ)
  LEFT OUTER JOIN MAT M ON M.ID=P.MATLIN   
WHERE 
  P.OBJ_ID  IN ( %(Condotta1)d,%(Condotta2)d,%(Condotta3)d,%(Condotta4)d,%(Condotta5)d,%(Condotta6)d,%(Condotta7)d,%(Condotta8)d)
  AND P.CODE in (1,2,4,91,92,93,94)
"""
SQLAllacci = """
SELECT DISTINCT
  P.*,
  Switch(
  P.OBJ_ID =%(Condotta1)d , 1,
  P.OBJ_ID =%(Condotta2)d , 2,
  P.OBJ_ID =%(Condotta3)d , 3,
  P.OBJ_ID =%(Condotta4)d , 4,
  P.OBJ_ID =%(Condotta5)d , 5,
  P.OBJ_ID =%(Condotta6)d , 6,
  P.OBJ_ID =%(Condotta7)d , 7,
  P.OBJ_ID =%(Condotta8)d , 8
  ) as IDSCHEDA,
  t.TIPFOG as TIPOFOGNA,
  P.IDPUNINI,
  P.IDPUNFIN,
  P.DISLINI,
  P.DISLFIN,
  P.QUOINI,
  P.QUOFIN,
  P.LARG_LIN * 10 AS LARGHEZZA,
  P.ALT_LIN  * 10 AS ALTEZZA,
  F.FORSEZ AS FORMA,
  M.MAT AS MATERIALE
FROM ((
  MASTER_L P LEFT OUTER JOIN TIPFOG T ON T.ID=P.TIPFOG)
    LEFT OUTER JOIN FORSEZ F ON F.ID=P.FORSEZ)
  LEFT OUTER JOIN MAT M ON M.ID=P.MATLIN   
WHERE 
  P.OBJ_ID  IN ( %(Condotta1)d,%(Condotta2)d,%(Condotta3)d,%(Condotta4)d,%(Condotta5)d,%(Condotta6)d,%(Condotta7)d,%(Condotta8)d)
  AND P.CODE = 3
"""


SQLImgdir = "select VALT from parametri where VAR ='IMGDIR'"
SQLComune = "select VALT from parametri where VAR ='COMUNE'"
SQLIstat = "select VALT from parametri where VAR ='ISTAT'"

S = c()
S.SQLScheda = SQLScheda
S.SQLPozzetto = SQLPozzetto
S.SQLPunto = SQLPunto
S.SQLTratte = SQLTratte
S.SQLAllacci = SQLAllacci
S.SQLImgdir = SQLImgdir
S.SQLComune = SQLComune
S.SQLIstat = SQLIstat


def test():
    pass


def basename(s):
    try:
        return os.path.basename(s)
    except:
        return ""


def dosqlquery(sql, conn):
    # ~ print sql
    ret = []
    cursor = conn.cursor()
    for row in cursor.execute(sql):
        data = rowtodict(row, cursor.description)
        ret.append(data)
    cursor.close()
    return ret


def domdb(dbfile, filter):
    # ~ DBfile = r'C:\SVIL\Geocomp\acad_tools\IDROLARIO\MONOGRAFIE\src\cortenova.mdb'
    conn = pyodbc.connect(
        'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=' + dbfile)
    S.basedir = os.path.dirname(dbfile)

    cursor = conn.cursor()

    S.imgdir = dosqlquery(S.SQLImgdir, conn)[0]["VALT"]
    S.comune = dosqlquery(S.SQLComune, conn)[0]["VALT"]
    S.comunedir = os.path.join(S.basedir, S.comune)
    S.pozzettidir = os.path.join(S.comunedir, "POZZETTI")
    mkdir(S.comunedir)
    mkdir(S.pozzettidir)
    # ~ print filter
    if filter == "ALL":
        sql = SQLScheda + WhereSchedaALL
    elif filter == "BIANCA":
        sql = SQLScheda + WhereSchedaBIANCA
    elif filter == "NERA":
        sql = SQLScheda + WhereSchedaNERA
    else:
        sql = SQLScheda + WhereSchedaSCHEDA % filter

    for row in cursor.execute(sql):  # cursors are iterable
        data = rowtodict(row, cursor.description)
        doScheda(conn, data)

    cursor.close()
    conn.close()


def rowtodict(data, descr):
    ret = {}
    for i in range(0, len(descr)):
        ret[descr[i][0]] = data[i]
    return ret


def doScheda(conn, data):
    data["rilevatore"] = "Geocomp"
    data["coox"] = "0"
    data["cooy"] = "0"
    data["srid"] = "UTM WGS84"
    data["srid"] = "UTM WGS84"
    data["plotimg"] = "Scheda%(scheda_numero)d.jpg" % data
    data["scheimg"] = "Schema%(scheda_numero)d.jpg" % data
    p = dosqlquery(SQLPozzetto % (data["id_pozzetto"]), conn)
    data["pozzetto"] = p[0]
    data["condotte"] = dosqlquery(SQLTratte % data, conn)
    data["allacci"] = dosqlquery(SQLAllacci % data, conn)

    p = dosqlquery(SQLPunto % (data["punto"]), conn)
    data["punto"] = p[0]

    curdir = os.path.join(S.pozzettidir, str(data["id_pozzetto"]))
    mkdir(curdir)

    data["outimg"] = basename(data["FotoEsterno"])
    data["imimg"] = basename(data["FotioInterno"])

    mv_to(data["FotoEsterno"], S.imgdir, curdir)
    mv_to(data["FotioInterno"], S.imgdir, curdir)
    mv_to(data["FotoComplessivo"], S.imgdir, curdir)
    mv_to(data["FotoAltro"], S.imgdir, curdir)
    mv_to(data["FotoEsterno1"], S.imgdir, curdir)
    mv_to(data["FotioInterno1"], S.imgdir, curdir)
    mv_to(data["FotoComplessivo1"], S.imgdir, curdir)
    mv_to(data["FotoAltro1"], S.imgdir, curdir)
    mv_to("Scheda%(scheda_numero)d.jpg" % data, S.basedir, curdir)
    mv_to("Schema%(scheda_numero)d.jpg" % data, S.basedir, curdir)

    templfname = template_name()
    # ~ print templfname
    templ = pyratemp.Template(
        filename=templfname, data=data, encoding='windows-1252')

    # ~ outhtml = os.path.join (curdir, "Scheda_%(scheda_numero)d.html" %data)
    outhtml = os.path.join(curdir, "Scheda.html")
    # ~ outpdf = os.path.join (curdir, "Scheda_%(scheda_numero)d.pdf" % data)
    outpdf = os.path.join(curdir, "Scheda.pdf")

    fout = codecs.open(outhtml, "w", encoding='windows-1252')
    fout.write(templ())
    fout.flush()
    fout.close()
    # subprocess.call(["wkhtmltopdf" , "--page-size A4", "orientation Portrait", outhtml, outpdf ])
    # subprocess.call(["wkhtmltopdf " , outhtml, outpdf ])
    subprocess.call(["wkhtmltopdf", "--background", "-s", "A4",
                     "--disable-smart-shrinking", "--dpi", "300", outhtml, outpdf])
    # subprocess.call(["wkhtmltopdf", "--background",  -s A4 --disable-smart-shrinking", outhtml, outpdf ])

    pass


def mkdir(p):
    try:
        os.mkdir(p)
    except:
        pass


def mv_to(fname, indir, outdir):
    try:
        # ~ print fname, indir ,outdir
        src = os.path.join(indir, os.path.basename(fname))
        dst = os.path.join(outdir, os.path.basename(fname))
        shutil.copyfile(src, dst)
    except:
        pass


def template_name():
    return os.path.join(module_path(), 'tmpl', "Scheda_template.html")


def execute_monografia(database=None, filtro="ALL"):

    if database is None:
        database = openFileDialog(
            extensions=[["*.mdb", "*.accdb", "database files"]], filename=module_path() , msg="Indica File Access da elaborare")
    if database is None:
        print("necessario indicare un file Access")
        return

    if isinstance(filtro, str):
        domdb(database, filtro)
    else:
        domdb(database, "ALL")


# def main():
#     parser = argparse.ArgumentParser(description="Consegna materiale")
#     parser.add_argument('-database', nargs=1, required=False,
#                         type=testfile, help='database')

#     parser.add_argument("-f", dest='filter', action='store', nargs=1,
#                         type=str,
#                         help='filtro pu essere BIANCA NERA ALL o un numero di scheda')

#     args = parser.parse_args()

#     # ~ print args
#     done = False

#     loaded = False
#     # ~ print  args

#     if args.database is None:
#         args.database = openFileDialog(
#             extensions=[["*.mdb", "*.accdb", "database files"]], filename=module_path() msg="Indica File Access da elaborare")
#     if args.database is None:
#         parser.print_help()
#         return

#     if args.filter:
#         domdb(args.dbfile[0], args.filter[0])
#     else:
#         domdb(args.dbfile[0], "ALL")


# # ~ if __name__ == "__main__": test()
# if __name__ == "__main__":
#     main()
