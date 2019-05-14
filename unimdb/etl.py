" etl main eleaborazione di rilevo su mdb realizato per uni_acque ma modificabile"
# 1168592
import os
import copy
import csv
import argparse
# import adodbapi
import pyodbc
from shapely.geometry import Point, LineString
from helpers import getcfg, we_are_frozen, testfile, module_relative_file, \
    module_relative, module_path, openFileDialog
import helpers.geometry as geo
# from helpers.geometry import mid_pt, distance, angle, txtangle, equal

import sqlparse
import ezdxf
import dbgshapefile as shapefile
import yaml
cfgfile, exist = module_relative_file('sql', 'config.yaml')
if exist:
    cfg = yaml.load(open(cfgfile))


class OperationException(Exception):
    " Eccezione "


class Operation (object):
    " Raccolta di operazioni sul db"

    def __init__(self, **kvargs):
        self.options = kvargs
        self._echo = False

    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        self._echo = bool(value)

    @property
    def silent(self):
        return not self._echo

    @silent.setter
    def silent(self, value):
        self._echo = not bool(value)

    def output(self, value):
        """output to console """
        if self._echo:
            if isinstance(value, str):
                print(value)
            elif hasattr(value, '__iter__'):
                for v in value:
                    print(v)
            else:
                print(value)

    def dispose(self):
        pass

    def finito(self):
        self.dispose()
        self.output("_______")
        self.output("FINITO")
        self.output("_______")


class reg(object):
    "classe per gestire record come oggetti deprecata"

    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row):
            setattr(self, attr, val)


class ShpDefinition(object):
    _shp_archi = {
        "defs": (
            {"name": "COD_CLASSE", "type": "C", "len": 6},
            {"name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"name": "RILIEVO", "type": "D"},
            {"name": "COM_ISTAT", "type": "C", "len": 8},
            {"name": "TP_STR_COD", "type": "C", "len": 8},
            {"name": "TP_STR_NOM", "type": "C", "len": 254},
            {"name": "ES_AMM_CF", "type": "C", "len": 2	},
            {"name": "L_EG_COD", "type": "C", "len": 16	},
            {"name": "L_EG_NOM", "type": "C", "len": 50	},
            {"name": "L_BORN", "type": "D"},
            {"name": "L_DIA", "type": "N", "len": 8, "dec": 0},
            {"name": "L_LUNG", "type": "N", "len": 11, "dec": 2, "calc": "lung"},
            {"name": "L_MAT", "type": "C", "len": 4},
            {"name": "L_STA", "type": "C", "len": 2},
            {"name": "L_PRO", "type": "C", "len": 2},
            {"name": "L_POS", "type": "C", "len": 2},
            {"name": "L_POS_SUP", "type": "C", "len": 2},
            {"name": "L_INFR_TY", "type": "C", "len": 2},
            {"name": "NODO_INI", "type": "N", "len": 19, "dec": 0},
            {"name": "NODO_FIN", "type": "N", "len": 19, "dec": 0},
            {"name": "L_F_TY", "type": "C", "len": 2},
            {"name": "L_F_TIPFOG", "type": "C", "len": 2},
            {"name": "L_F_TIPLIN", "type": "C", "len": 2},
            {"name": "L_F_FORSEZ", "type": "C", "len": 2},
            {"name": "L_F_LARG", "type": "N", "len": 11, "dec": 2},
            {"name": "L_F_ALT", "type": "N", "len": 11, "dec": 2},
        ),
        "name": "C070201",
    }
    _shp_nodi = {
        "name": "C070202",
        "defs": (
            {"name": "COD_CLASSE", "type": "C", "len": 6},
            {"name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"name": "RILIEVO", "type": "D"},
            {"name": "P_BORN", "type": "D"},
            {"name": "P_MAT", "type": "C", "len": 4},
            {"name": "P_STA", "type": "C", "len": 2},
            {"name": "P_QUO", "type": "N", "len": 7, "dec": 2},
            {"name": "P_POS", "type": "C", "len": 2},
            {"name": "P_UTE", "type": "C", "len": 2},
            {"name": "P_F_TY", "type": "C", "len": 4},
            {"name": "P_F_REC", "type": "C", "len": 2},
        ),
    }

    def __init__(self, **kvargs):
        self._path = ""
        config = getcfg()
        cfg = config.get("dxf2shp", {}).get("shp_archi", None)
        self.handler_shp_archi = None
        self.handler_shp_nodi = None

        if cfg:
            self.shp_archi = cfg
        else:
            self.shp_archi = self._shp_archi
        cfg = config.get("dxf2shp", {}).get("shp_nodi", None)
        if cfg:
            self.shp_nodi = cfg
        else:
            self.shp_nodi = self._shp_nodi

    @property
    def shp_path(self):
        return self._path

    @shp_path.setter
    def shp_path(self, value):
        self._path = value

    def initshp(self, path=None):

        if path is not None:
            self._path = path
        """ inizializza gli shape file """
        # self._dwg.filename = self.dxfdatabase
        # C070201
        # C070202
        pozzi_defs = self.shp_nodi["defs"]
        self.handler_shp_archi = shapefile.Writer(target=os.path.join(
            self._path, self.shp_archi["name"]), shapeType=shapefile.POLYLINE)
        self.handler_shp_nodi = shapefile.Writer(target=os.path.join(
            self._path, self.shp_nodi["name"]), shapeType=shapefile.POINT)

        self._tubi_defs = self.shp_archi["defs"]
        self._tubi_atts = ([x["name"] for x in self.shp_archi["defs"]])

        self._pozzi_atts = ([x["name"] for x in self.shp_nodi["defs"]])

        for f in self.shp_archi["defs"]:
            name = f.get("name", None)
            stype = f.get("type", "C")
            lun = f.get("lun", "30")
            dec = f.get("dec", 0)
            self.handler_shp_archi.field(name, fieldType=stype, size=lun, decimal=dec)

        for f in self.shp_nodi["defs"]:

            name = f.get("name", None)
            stype = f.get("type", "C")
            lun = f.get("len", "30")
            dec = f.get("dec", 0)
            self.handler_shp_nodi.field(name, fieldType=stype, size=lun, decimal=dec)

    def add_nodo(self, x, y, attributi):
        self.handler_shp_nodi.point(x, y)
        self.handler_shp_nodi.record(**attributi)

    def add_arco(self, pts, attributi):
        self.handler_shp_archi.line([pts])
        self.handler_shp_archi.record(**attributi)

    def saveshp(self):
        """ Salva gli shape file"""
        # self._dwg.filename = self.dxfdatabase
        if self.handler_shp_archi is not None:
            self.handler_shp_archi.close()
        if self.handler_shp_nodi is not None:
            self.handler_shp_nodi.close()

    def dispose(self):
        self.saveshp()


def getcolumn(cursor, row, attribute):
    """data la descrizione del cursore e la riga cerca l'attributo
        @param cursor : cursor returned by query
        @param row : sequence a singole row returnde by fetch or fetch all
        @param attribute : str
    """
    for (attr, val) in zip((d[0] for d in cursor.description), row):
        if attr == attribute:
            return val
    return None


def convert_value(value, type=None, len=None, dec=None, **kvaargs):
    if type is None:
        return None
    elif type == 'C':
        return str(value)
    elif type == 'D':
        return None
    elif type == 'N':
        if dec == 0 or dec is None:
            try:
                return int(value)
            except Exception as identifier:
                return None
        else:
            try:
                return float(value)
            except Exception as identifier:
                return None


class DxfOperation (Operation, ShpDefinition):
    """ OPERAZIONI SU DxF
    """
    _dxf_archi = {
        "layers": (
            "20_RETE-FOGNATURA-NERA",
            "20_RETE-FOGNATURA-BIANCA",
            "20_RETE-FOGNATURA-MISTA",
            "20_RETE-ALLACCIAMENTO",
            "20_RETE-SCOLMATORE",
            "20_RETE-METEORICHE-STRADALI",
            "20_RETE-COLLETTORE-MISTA-SOVR",
            "20_F-TRATTO FUORI SERVIZIO",
            "20_RETE-FOSSI",
        ),
        "atts": ('OBJ_ID', 'ISTAT_ID', 'CODE', 'IDPUNINI', 'IDPUNFIN', 'IDLININI', 'MATLIN', 'FORSEZ',
                 'ALT_LIN', 'LARG_LIN', 'QUOINI', 'QUOFIN', 'DISLINI', 'DISLFIN', 'TIPFOG', 'TIPLINIDR',
                 'POS_TRATTA', 'POS_SUP', 'IMAGE', 'DATA', 'NOTE', 'LUNG', 'PENDENZA', 'DEN_TRONC',
                 ),
        "element": "LWPOLYLINE",
        "mapping": (
            {"att": "CODE", "name": "COD_CLASSE", "type": "C", "len": 6},
            {"att": "IMAGE", "name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"att": "", "name": "RILIEVO", "type": "D"},
            {"att": "ISTAT_ID", "name": "COM_ISTAT", "type": "C", "len": 8},
            {"att": "", "name": "TP_STR_COD", "type": "C", "len": 8},
            {"att": "", "name": "TP_STR_NOM", "type": "C", "len": 254},
            {"att": "", "name": "ES_AMM_CF", "type": "C", "len": 2	},
            {"att": "", "name": "L_EG_COD", "type": "C", "len": 16	},
            {"att": "", "name": "L_EG_NOM", "type": "C", "len": 50	},
            {"att": "", "name": "L_BORN", "type": "D"},
            {"att": "LARG_LIN", "name": "L_DIA", "type": "N", "len": 8, "dec": 0},
            {"att": "LUNG", "name": "L_LUNG", "type": "N", "len": 11, "dec": 2, "calc": "lung"},
            {"att": "MATLIN", "name": "L_MAT", "type": "C", "len": 4},
            {"att": "", "name": "L_STA", "type": "C", "len": 2},
            {"att": "DISLINI", "name": "L_PRO", "type": "C", "len": 2},
            {"att": "POS_TRATTA", "name": "L_POS", "type": "C", "len": 2},
            {"att": "POS_SUP", "name": "L_POS_SUP", "type": "C", "len": 2},
            {"att": "", "name": "L_INFR_TY", "type": "C", "len": 2},
            {"att": "", "name": "NODO_INI", "type": "N", "len": 19, "dec": 0},
            {"att": "", "name": "NODO_FIN", "type": "N", "len": 19, "dec": 0},
            {"att": "", "name": "L_F_TY", "type": "C", "len": 2},
            {"att": "TIPFOG", "name": "L_F_TIPFOG", "type": "C", "len": 2},
            {"att": "TIPLINIDR", "name": "L_F_TIPLIN", "type": "C", "len": 2},
            {"att": "FORSEZ", "name": "L_F_FORSEZ", "type": "C", "len": 2},
            {"att": "LARG_LIN", "name": "L_F_LARG", "type": "N", "len": 11, "dec": 2},
            {"att": "ALT_LIN", "name": "L_F_ALT", "type": "N", "len": 11, "dec": 2},
        ),
        "block": {
            "layers": ("20_F-BLK-CONDOTTE",),
            "names": ("MASTER_S_L_CONDOTTA",)
        },
    }
    _dxf_nodi = {
        "element": "INSERT",
        "atts": ('OBJ_ID', 'ISTAT_ID', 'QUOPUN', 'CODE', 'FORMA_CHIU', 'MAT_CHIU', 'LARG_CHIU', 'LUNG_CHIU', 'FORMA_SUP', 'MAT_SUP', 'LARG_SUP',
                 'LUNG_SUP', 'FORMA_INF', 'LARG_INF', 'LUNG_INF', 'MAT_INF', 'QUOINFPOZ', 'COLPOZ', 'TRAVASO', 'COP_CHIU', 'APP_CHIU', 'MAT_COLPOZ',
                 'SUPPOSA', 'POS_NODO', 'POS_SUP', 'QUOTERR', 'QUOTRAVASO', 'IMAGE', 'DISEGNI', 'DATA', 'NOTE', 'DEN_PUN', 'SPES_SUP',
                 ),
        "layers": (
            "20_F-POZZETTI-VARI",
            "20_F-CAMERETTA-SFIORATORE",
            "20_F-CAMERETTE",
            "20_F-DEPURATORE",
            "20_F-DISOLEATORI",
            "20_F-DN-CONDOTTE",
            "20_F-NODO-CDN",
            "20_F-NODO-INT",
            "20_F-NODO-MATERIALE",
            "20_F-POZZETTI-VARI",
            "20_F-SCARICO",
        ),
        "unused": (
            "20_F-ETICHETTA-POZZETTO",
            "20_F-TRATTO FUORI SERVIZIO",
            "20_F-VASCA-PP",
        ),
        "mapping": (
            {"att": "CODE", "name": "COD_CLASSE", "type": "C", "len": 6},
            {"att": "IMAGE", "name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"att": "", "name": "RILIEVO", "type": "D"},
            {"att": "", "name": "P_BORN", "type": "D"},
            {"att": "MAT_SUP", "name": "P_MAT", "type": "C", "len": 4},
            {"att": "", "name": "P_STA", "type": "C", "len": 2},
            {"att": "QUOTERR", "name": "P_QUO", "type": "N", "len": 7, "dec": 2},
            {"att": "POS_NODO", "name": "P_POS", "type": "C", "len": 2},
            {"att": "", "name": "P_UTE", "type": "C", "len": 2},
            {"att": "", "name": "P_F_TY", "type": "C", "len": 4},
            {"att": "", "name": "P_F_REC", "type": "C", "len": 2},
        ),
        "block": {
            "layers": ("20_F-POZZETTI-VARI",),
            "names": ("PF",),
        },
    }

    def __init__(self, **kvargs):
        Operation.__init__(self, **kvargs)
        ShpDefinition.__init__(self, **kvargs)
        self.echo = True
        self._dxfin = kvargs.get("dxf", None)

        if self._dxfin is None:
            raise OperationException("parametro dxf mancante inizializzazndo una DxfOperation")
        ezdxf.options.templatedir = module_relative('dxf')
        self._dwg = None
        self._archi = []
        self._nodi = []
        self.shp_path = os.path.dirname(self._dxfin)
        config = getcfg()
        cfg = config.get("dxf2shp", {}).get("dxf_archi", None)
        if cfg:
            self.dxf_archi = cfg
        else:
            self.dxf_archi = self._dxf_archi
        cfg = config.get("dxf2shp", {}).get("dxf_nodi", None)
        if cfg:
            self.dxf_nodi = cfg
        else:
            self.dxf_nodi = self._dxf_nodi

        self.initshp()

    def opendxf(self):
        self._dwg = ezdxf.readfile(self._dxfin)
        self._modelspace = self._dwg.modelspace()

    def closedxf(self):
        del self._dwg
        del self._modelspace
        self._dwg = None
        self._modelspace = None

    def writeshp(self):
        self.opendxf()
        nodi = self.getnodi()
        markers = self.getmarkers()
        archi = self.getarchi()
        self.closedxf()
        for arco in archi:
            for mark in markers:
                if arco["geom"].distance(mark["geom"]) < 0.002:
                    arco["marker"] = mark
                    markers.remove(mark)
                    break
        for arco in archi:
            self.write_arco(arco)
        for nodo in nodi:
            self.write_nodo(nodo)

    def getnodi(self):
        nodi = []
        for layer in self.dxf_nodi["layers"]:
            blockrefs = self._modelspace.query('INSERT[layer=="%s"]' % layer)
            for entity in blockrefs:
                nodo = {
                    "geom": Point(entity.dxf.insert[0], entity.dxf.insert[1]),
                    "x": entity.dxf.insert[0],
                    "y": entity.dxf.insert[1],
                }
                for attrib in entity.attribs():
                    nodo[attrib.dxf.tag] = attrib.dxf.text
                nodi.append(nodo)
            del blockrefs
        return nodi

    def getmarkers(self):
        nodi = []
        for layer in self.dxf_archi["block"]["layers"]:
            for name in self.dxf_archi["block"]["names"]:
                blockrefs = self._modelspace.query('INSERT[layer=="%s" & name == "%s"]' % (layer, name))
                for entity in blockrefs:
                    nodo = {
                        "geom": Point(entity.dxf.insert[0], entity.dxf.insert[1]),
                        "x": entity.dxf.insert[0],
                        "y": entity.dxf.insert[1],
                    }
                    for attrib in entity.attribs():
                        nodo[attrib.dxf.tag] = attrib.dxf.text
                    nodi.append(nodo)
                del blockrefs
        return nodi

    def getarchi(self):
        """ carica dal dxf le geometrie delle condotte
        """
        archi = []
        for layer in self.dxf_archi["layers"]:
            res = self._modelspace.query('LWPOLYLINE[layer=="%s"]' % layer)
            for pline in res:
                pts = [(x[0], x[1]) for x in pline]
                arco = {
                    "marker": None,
                    "geom": LineString(pts),
                    "pts": pts,
                }
                archi.append(arco)
            del res
        return archi

    def dispose(self):
        """ salva tutto
        """
        Operation.dispose(self)
        ShpDefinition.dispose(self)

    def __del__(self):
        """assicira di salvar tutto"""
        self.dispose()

    def write_nodo(self, nodo):
        """
        scrive il bloccco dei pozzeetti
        """
        x = nodo["x"]
        y = nodo["y"]
        attr = {}
        for map_att in self.dxf_nodi["mapping"]:
            if map_att["att"] != "":
                val = nodo.get(map_att["att"], None)
                if val is not None:
                    attr[map_att["name"]] = convert_value(val, **map_att)
                else:
                    attr[map_att["name"]] = None
            else:
                attr[map_att["name"]] = None
        self.add_nodo(x, y, attr)

    def write_arco(self, arco):
        """ scrive  un arco """
        coords = arco["pts"]
        attr = {}
        if arco["marker"] is not None:
            for map_att in self.dxf_archi["mapping"]:
                if map_att["att"] != "":
                    val = arco["marker"].get(map_att["att"], None)
                    if val is not None:
                        attr[map_att["name"]] = convert_value(val, **map_att)
                    else:
                        attr[map_att["name"]] = None
                else:
                    attr[map_att["name"]] = None

        self.add_arco(coords, attr)


class MdbOperation (Operation):
    """ oPERAZIONI SU MDB
    """

    def __init__(self, **kvargs):
        Operation.__init__(self, **kvargs)
        ezdxf.options.templatedir = module_relative('dxf')
        self.conn = None
        self._dwg = None
        self._geometries = []
        if "database" in self.options:
            self.connect(self.options["database"])
            self.initshp()
        else:
            raise OperationException(
                "parametro database mancante inizializzazndo una MdbOperation")
        self._silent = True
        self._echo = False

    def get_lines(self, fname):
        """ carica dal dxf le geometrie delle condotte
        """
        reti = (
            '20_RETE-FOGNATURA-NERA',
            '20_RETE-FOGNATURA-BIANCA',
            '20_RETE-FOGNATURA-MISTA',
            '20_RETE-ALLACCIAMENTO',
            '20_RETE-SCOLMATORE',
            '20_RETE-METEORICHE-STRADALI',
            '20_RETE-COLLETTORE-MISTA-SOVR',
            '20_RETE-FOSSI',
        )
        dwg = ezdxf.readfile(fname)
        ms = dwg.modelspace()
        for layer in reti:
            res = ms.query('LWPOLYLINE[layer=="%s"]' % layer)
            for pline in res:
                # pts = [x for x in pline]
                pts = [(x[0], x[1]) for x in pline]
                self._geometries.append(pts)
        del res
        del ms
        del dwg

    def get_coordinates(self, start, end):
        """ cerca le coordinate di una linea che mecci i punti start ed end"""
        for i in range(len(self._geometries)):
            ln = self._geometries[i]
            s = ln[0]
            e = ln[-1]
            if geo.equal(start, s) and geo.equal(end, e):
                ln = self._geometries.pop(i)
                ln[0] = start
                ln[-1] = end
                return ln
        return [start, end]

    @property
    def silent(self):
        return self.silent

    @silent.setter
    def silent(self, value):
        self._silent = value

    @property
    def echo(self):
        return self._echo

    @echo.setter
    def echo(self, value):
        self._echo = value

    def connect(self, database):
        """connect to database e imposta nome del dxf
        """
        self.database = database
        self.dxfdatabase = database + '.dxf'
        # self.constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source=%s'  % self.database
        # self.constr = 'Provider=Microsoft.ACE.OLEDB.12.0;Data Source=%s; Persist Security Info=False;' % self.database
        # self.conn = adodbapi.connect(self.constr)
        self.constr = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)}; Dbq=%s; Uid=Admin; Pwd=; ExtendedAnsiSQL=1;' % self.database
        self.conn = pyodbc.connect(self.constr)

    def dispose(self):
        """ salva tutto
        """
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            del self.conn
            self.conn = None

        if self._dwg is not None:
            self._dwg.save()
            self._dwg = None
        self.saveshp()

    def __del__(self):
        """assicira di salvar tutto"""
        self.dispose()

    def updatecondotta(self, objid, lung):
        sqlstatement = "update condotte set tlung = %f where ID_key=%d" % (
            lung, objid)
        if self._echo:
            self.output(sqlstatement)
        cur = self.conn.cursor()
        cur.execute(sqlstatement)
        self.conn.commit()
        # cur.execute('commit;')
        cur.close()

    def sql(self, sqlstatement):
        """ sesegue sql"""
        self.output(sqlstatement)
        if self._echo:
            self.output(sqlstatement)
        cur = self.conn.cursor()
        cur.execute(sqlstatement)
        if not self._silent:
            result = cur.fetchall()
            self.output(result)
        self.conn.commit()
        # cur.execute('commit;')
        cur.close()
        return result

    def filesql(self, fname):
        """ esegue uno script sql """
        cur = self.conn.cursor()
        f = open(fname, "r")
        sqls = f.read()
        # stmnts = sqlparse.split(sqls)
        stmnts = sqlparse.parse(sqls)
        for s in stmnts:
            try:
                stype = s.get_type()
                if stype == 'UNKNOWN':
                    continue
                ssql = s.normalized
                if self._echo:
                    self.output(ssql)
                cur.execute(ssql)
                if stype == 'SELECT':
                    result = cur.fetchall()
                    if not self._silent:
                        self.output(result)
                self.conn.commit()

                self.output('OK')
            except Exception as ex:
                self.output(" ERRORE %s " % ex.__str__())
                # if not self._silent:
                #     self.output (" ERRORE %s " % ex.message)
        # cur.execute('commit;')
        cur.close()

    def filecsv(self, fname):
        """carica un csv di unri"""
        cur = self.conn.cursor()
        sql = 'insert into punti (OBJECTID, X , Y , Z  ) values ( ? , ?, ?, ?);'
        with open(fname, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                param = (str(row[0]), float(row[1]),
                         float(row[2]), float(row[3]))
                cur.execute(sql, param)
            # cur.executemany(sql, reader)
            # for row in spamreader:
        # cur.execute('commit;')
        self.conn.commit()
        cur.close()

    def initdxf(self):
        """ inizializza il dxf dal template"""

        self._dwg = ezdxf.readfile(
            module_relative_file('dxflib', 'base.dxf')[0])
        self._dwg.saveas(self.dxfdatabase)
        self._dwg.appids.new('PE_URL')  # create APP ID entry

        # self._dwg.filename = self.dxfdatabase

    def initshp(self):
        """ inizializza gli shape file """
        outdir = os.path.dirname(self.database)
        # self._dwg.filename = self.dxfdatabase
        # C070201
        tubi_defs = (
            {"name": "COD_CLASSE", "type": "C", "len": 6},
            {"name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"name": "RILIEVO", "type": "D"},
            {"name": "COM_ISTAT", "type": "C", "len": 8},
            {"name": "TP_STR_COD", "type": "C", "len": 8},
            {"name": "TP_STR_NOM", "type": "C", "len": 254},
            {"name": "ES_AMM_CF", "type": "C", "len": 2	},
            {"name": "L_EG_COD", "type": "C", "len": 16	},
            {"name": "L_EG_NOM", "type": "C", "len": 50	},
            {"name": "L_BORN", "type": "D"},
            {"name": "L_DIA", "type": "N", "len": 8, "dec": 0},
            {"name": "L_LUNG", "type": "N", "len": 11, "dec": 2, "calc": "lung"},
            {"name": "L_MAT", "type": "C", "len": 4},
            {"name": "L_STA", "type": "C", "len": 2},
            {"name": "L_PRO", "type": "C", "len": 2},
            {"name": "L_POS", "type": "C", "len": 2},
            {"name": "L_POS_SUP", "type": "C", "len": 2},
            {"name": "L_INFR_TY", "type": "C", "len": 2},
            {"name": "NODO_INI", "type": "N", "len": 19, "dec": 0},
            {"name": "NODO_FIN", "type": "N", "len": 19, "dec": 0},
            {"name": "L_F_TY", "type": "C", "len": 2},
            {"name": "L_F_TIPFOG", "type": "C", "len": 2},
            {"name": "L_F_TIPLIN", "type": "C", "len": 2},
            {"name": "L_F_FORSEZ", "type": "C", "len": 2},
            {"name": "L_F_LARG", "type": "N", "len": 11, "dec": 2},
            {"name": "L_F_ALT", "type": "N", "len": 11, "dec": 2},
        )
        # C070202
        pozzi_defs = (
            {"name": "COD_CLASSE", "type": "C", "len": 6},
            {"name": "FILE_ID", "type": "N", "len": 19, "dec": 0},
            {"name": "RILIEVO", "type": "D"},
            {"name": "P_BORN", "type": "D"},
            {"name": "P_MAT", "type": "C", "len": 4},
            {"name": "P_STA", "type": "C", "len": 2},
            {"name": "P_QUO", "type": "N", "len": 7, "dec": 2},
            {"name": "P_POS", "type": "C", "len": 2},
            {"name": "P_UTE", "type": "C", "len": 2},
            {"name": "P_F_TY", "type": "C", "len": 4},
            {"name": "P_F_REC", "type": "C", "len": 2},
        )
        self._shp_tubi = shapefile.Writer(target=os.path.join(
            outdir, "C070201"), shapeType=shapefile.POLYLINE)
        self._shp_pozzi = shapefile.Writer(target=os.path.join(
            outdir, "C070202"), shapeType=shapefile.POINT)

        self._tubi_defs = tubi_defs
        self._tubi_atts = ([x["name"] for x in tubi_defs])
        self._pozzi_atts = ([x["name"] for x in pozzi_defs])
        for f in tubi_defs:
            name = f.get("name", None)
            stype = f.get("type", "C")
            lun = f.get("lun", "30")
            dec = f.get("dec", 0)
            self._shp_tubi.field(name, fieldType=stype, size=lun, decimal=dec)
        for f in pozzi_defs:
            name = f.get("name", None)
            stype = f.get("type", "C")
            lun = f.get("lun", "30")
            dec = f.get("dec", 0)
            self._shp_pozzi.field(name, fieldType=stype, size=lun, decimal=dec)

    def saveshp(self):
        """ Salva gli shape file"""
        outdir = os.path.dirname(self.database)
        # self._dwg.filename = self.dxfdatabase
        if self._shp_tubi is not None:
            self._shp_tubi.close()
            # self._shp_tubi.save(target=os.path.join(outdir, "C070201"))
        if self._shp_pozzi is not None:
            self._shp_pozzi.close()
            # self._shp_pozzi.save(target=os.path.join(outdir, "C070202"))

    def write_pozzo(self, cursor):
        """
        scrive il bloccco dei pozzeetti
        """
        modelspace = self._dwg.modelspace()
        for bl in cursor.fetchall():
            # rec = reg(cursor, bl)
            atts = ('OBJ_ID', 'ISTAT_ID', 'QUOPUN', 'CODE', 'FORMA_CHIU', 'MAT_CHIU', 'LARG_CHIU', 'LUNG_CHIU', 'FORMA_SUP', 'MAT_SUP', 'LARG_SUP',
                    'LUNG_SUP', 'FORMA_INF', 'LARG_INF', 'LUNG_INF', 'MAT_INF', 'QUOINFPOZ', 'COLPOZ', 'TRAVASO', 'COP_CHIU', 'APP_CHIU', 'MAT_COLPOZ',
                    'SUPPOSA', 'POS_NODO', 'POS_SUP', 'QUOTERR', 'QUOTRAVASO', 'IMAGE', 'DISEGNI', 'DATA', 'NOTE', 'DEN_PUN', 'SPES_SUP',
                    )
            layer = getcolumn(cursor, bl, 'LAYER')
            if layer is None:
                layer = '20_F-POZZETTI-VARI'

            dxfvals = {
                'layer': layer
            }

            blocco = getcolumn(cursor, bl, 'BLOCCO')
            if blocco is None:
                blocco = 'PF'

            # modelspace.add_auto_blockref(
            # insert = (rec.X, rec.Y)
            x, y = (getcolumn(cursor, bl, 'X'), getcolumn(cursor, bl, 'Y'))
            insert = (x, y)
            block = modelspace.add_blockref(blocco, insert, dxfattribs=dxfvals)
            insert = (x + 2, y + 2)
            for tag in atts:
                # text = rec.__getattribute__(tag)
                text = getcolumn(cursor, bl, tag)
                if text is None:
                    text = ''
                att = block.add_attrib(tag, text, insert, dxfattribs=dxfvals)
                if tag != 'OBJ_ID':
                    att.is_invisible = True
            nfoto = 1.5
            foto_e = getcolumn(cursor, bl, 'FOTO_E')
            if foto_e is not None:
                # fotos = rec.FOTO_E
                if isinstance(foto_e, str):
                    ff = foto_e.split(",")
                    for foto in ff:
                        txt = foto + ".jpeg"
                        url = ".\\foto\\" + txt
                        self.add_link(x + 6, y + nfoto,
                                      txt, url, layer)
                        nfoto = nfoto + 1.5

            foto_i = getcolumn(cursor, bl, 'FOTO_I')
            if foto_i is not None:
                # fotos = rec.FOTO_I
                if isinstance(foto_i, str):
                    ff = foto_i.split(",")
                    for foto in ff:
                        txt = foto + ".jpeg"
                        url = ".\\foto\\" + txt
                        self.add_link(x + 6, y + nfoto,
                                      txt, url, layer)
                        nfoto = nfoto + 1.5

        pass

    def _query_do(self, callback, query):
        """ esegue query  richiama callback
        """
        cur = self.conn.cursor()
        f = open(module_relative_file('sql', query)[0], "r")
        sqls = f.read()
        # stmnts = sqlparse.split(sqls)
        stmnts = sqlparse.parse(sqls)
        for s in stmnts:
            try:
                stype = s.get_type()
                if stype == 'UNKNOWN':
                    continue
                ssql = s.normalized
                if self._echo:
                    self.output(ssql)
                cur.execute(ssql)
                if stype == 'SELECT':
                    callback(cur)
                self.conn.commit()
                if self._echo:
                    self.output('OK')
            except Exception as ex:
                self.output(" ERRORE %s " % ex.__str__())
        cur.close()

    def query_pozzi(self):
        """ esegue query dei pozzetti e richiama write su dxf
        """
        self.output(" dxf Pozzi")
        self._query_do(self.write_pozzo, 'pozzi.sql')

    def write_tubo(self, cursor):
        """
        scrive il bloccco del tubo
        """
        modelspace = self._dwg.modelspace()
        for bl in cursor.fetchall():
            # rec = reg(cursor, bl)
            atts = ('OBJ_ID', 'ISTAT_ID', 'CODE', 'IDPUNINI', 'IDPUNFIN', 'IDLININI', 'MATLIN', 'FORSEZ',
                    'ALT_LIN', 'LARG_LIN', 'QUOINI', 'QUOFIN', 'DISLINI', 'DISLFIN', 'TIPFOG', 'TIPLINIDR',
                    'POS_TRATTA', 'POS_SUP', 'IMAGE', 'DATA', 'NOTE', 'LUNG', 'PENDENZA', 'DEN_TRONC',
                    'SEQ', 'ENTRA', 'ESCE', 'DAPOZZO', 'VERSOPOZZO',
                    )
            dxfvals = {'layer': '0'}
            x1, y1 = (getcolumn(cursor, bl, 'X1'), getcolumn(cursor, bl, 'Y1'))
            x, y = (getcolumn(cursor, bl, 'X'), getcolumn(cursor, bl, 'Y'))
            insert = (x1, y1)
            block = modelspace.add_blockref(
                'MASTER_S_L_CONDOTTA', insert, dxfattribs=dxfvals)
            insert = (x1 + 2, y1 + 2)
            for tag in atts:
                # text = rec.__getattribute__(tag)
                text = getcolumn(cursor, bl, tag)
                if text is None:
                    text = ''
                att = block.add_attrib(tag, text, insert, dxfattribs=dxfvals)
                if tag != 'OBJ_ID':
                    att.is_invisible = True
            dxfvals = {'layer': '0'}
            # line = modelspace.add_line( (rec.X, rec.Y), (rec.X1, rec.Y1), dxfattribs=dxfvals)
            points = [(x, y), (x1, y1)]
            modelspace.add_lwpolyline(points, dxfattribs=dxfvals)

    def query_tubi(self):
        """ esegue query dei tubi e richiama write su dxf
        """
        self.output(" dxf Tubi entranti o uscenti dai pozzi")

        self._query_do(self.write_tubo, 'tubi.sql')

    def add_link(self, x, y, text, url, layer):
        modelspace = self._dwg.modelspace()
        opt = {
            'layer': layer,
            'rotation': 0.0,
            'height': 1.5}
        # text = modelspace.add_text(text, dxfattribs=opt).set_pos((x, y), align='BOTTOM_CENTER')
        # text = modelspace.add_text(text, dxfattribs=opt).set_pos((x, y), align='BOTTOM_CENTER').tags.new_xdata(
        #     'PE_URL', [(1000, url), (1002, "{"), (1000, text), (1002, "}")])

        text = modelspace.add_text(
            text, dxfattribs=opt) .set_pos(
                (x, y), align='BOTTOM_CENTER').tags.new_xdata('PE_URL',
                                                              [
                                                                  (1000, url),
                                                                  (1002, '{'),
                                                                  (1000, text),
                                                                  (1002, '{'),
                                                                  (1071, 1),
                                                                  (1002, '}'),
                                                                  (1002, '}')
                                                              ])

    def write_condotta(self, cursor):
        """
        scrive il 0bloccco del tubo
        """
        bckgeom = copy.deepcopy(self._geometries)
        modelspace = self._dwg.modelspace()
        for bl in cursor.fetchall():
            id_key = getcolumn(cursor, bl, 'ID_KEY')
            x, y = (getcolumn(cursor, bl, 'X'), getcolumn(cursor, bl, 'Y'))
            x1, y1 = (getcolumn(cursor, bl, 'X1'), getcolumn(cursor, bl, 'Y1'))
            # rec = reg(cursor, bl)
            atts = ('OBJ_ID', 'ISTAT_ID', 'CODE', 'IDPUNINI', 'IDPUNFIN', 'IDLININI', 'MATLIN', 'FORSEZ',
                    'ALT_LIN', 'LARG_LIN', 'QUOINI', 'QUOFIN', 'DISLINI', 'DISLFIN', 'TIPFOG', 'TIPLINIDR',
                    'POS_TRATTA', 'POS_SUP', 'IMAGE', 'DATA', 'NOTE', 'LUNG', 'PENDENZA', 'DEN_TRONC',
                    )
            layer = getcolumn(cursor, bl, 'LAYER')
            if layer is None:
                layer = '20_RETE-FOGNATURA-MISTA'

            dxfvals = {
                'layer': '20_F-BLK-CONDOTTE'
            }

            coordinates = self.get_coordinates((x, y), (x1, y1))
            lung = geo.ln_length(coordinates)
            try:
                # pend = float(rec.DH) / lung * 100
                pend = float(getcolumn(cursor, bl, 'DH')) / lung * 100
            except Exception as e:
                pend = 0
            self.updatecondotta(id_key, lung)
            insert, alpha = geo.mid_a_ln(coordinates)
            block = modelspace.add_blockref(
                'MASTER_S_L_CONDOTTA', insert, dxfattribs=dxfvals)
            insertt = geo.add_scalar(insert, 2)
            for tag in atts:
                # text = rec.__getattribute__(tag)
                text = getcolumn(cursor, bl, tag)
                if text is None:
                    text = ''
                if tag == 'LUNG':
                    text = "%.3f" % lung
                if tag == 'PENDENZA':
                    text = "%.3f" % pend
                att = block.add_attrib(tag, text, insertt, dxfattribs=dxfvals)
                if tag != 'OBJ_ID':
                    att.is_invisible = True
            dxfvals = {'layer': layer}
            # line = modelspace.add_line( (rec.X, rec.Y), (rec.X1, rec.Y1), dxfattribs=dxfvals)
            modelspace.add_lwpolyline(coordinates, dxfattribs=dxfvals)
            sec = getcolumn(cursor, bl, 'SECONDARY')
            # if hasattr(rec, 'SECONDARY'):
            if sec is not None:
                opt = {'layer': layer,
                       'rotation': alpha,
                       'height': 1.7}
                text = modelspace.add_text(sec, dxfattribs=opt).set_pos(
                    insert, align='BOTTOM_CENTER')
        self._geometries = bckgeom

    def query_condotte(self):
        """ esegue query dei tubi e richiama write su dxf
        """
        self.output("dxf Condotte")

        self._query_do(self.write_condotta, 'condotte.sql')

    def write_shp_pozzo(self, cursor):
        """
        scrive il bloccco dei pozzeetti
        """
        shp = self._shp_pozzi
        atts = self._pozzi_atts

        for bl in cursor.fetchall():
            x, y = (getcolumn(cursor, bl, 'X'), getcolumn(cursor, bl, 'Y'))
            # rec = reg(cursor, bl)
            # add point (
            shp.point(x, y)
            recdict = {}
            for key in atts:
                # recdict[key] = rec.__getattribute__(key)
                recdict[key] = getcolumn(cursor, bl, key)

            shp.record(**recdict)

    def query_shp_pozzi(self):
        """ esegue query per shp  pozzetti e richiama write su shp
        """
        self.output(" shape Pozzi")

        self._query_do(self.write_shp_pozzo, 'shp_pozzi.sql')

    def write_shp_condotta(self, cursor):
        """
        scrive il bloccco dei pozzeetti
        """
        shp = self._shp_tubi
        # atts = self._tubi_atts
        defs = self._tubi_defs

        for bl in cursor.fetchall():
            x, y = (getcolumn(cursor, bl, 'X'), getcolumn(cursor, bl, 'Y'))
            x1, y1 = (getcolumn(cursor, bl, 'X1'), getcolumn(cursor, bl, 'Y1'))
            # rec = reg(cursor, bl)
            coordinates = self.get_coordinates((x, y), (x1, y1))
            lung = geo.ln_length(coordinates)
            dh = getcolumn(cursor, bl, 'DH')
            if dh:
                pend = float(dh) / lung * 100
            else:
                pend = 0

            # add point (
            shp.line([coordinates])
            recdict = {}
            for tdef in defs:
                key = tdef["name"]
                calc = tdef.get("calc", '')
                if calc == 'lung':
                    recdict[key] = lung
                elif calc == 'pend':
                    recdict[key] = pend
                else:
                    recdict[key] = getcolumn(cursor, bl, key)
                    # recdict[key] = rec.__getattribute__(key)
            shp.record(**recdict)

    def query_shp_condotte(self):
        """ esegue query per shp  pozzetti e richiama write su shp
        """
        self.output(" shape Condotte")
        self._query_do(self.write_shp_condotta, 'shp_condotte.sql')


def execute_dxf2shp(dxf=None):
    """ execute db 2 dxf etl """

    if dxf is None:
        dxf = openFileDialog(extensions=[["*.dxf", "dxf files"]], filename=" * .dxf", msg="Disegno come dxf")

    op = DxfOperation(dxf=dxf)
    op.echo = True
    op.writeshp()
    op.finito()


def execute_db2dxf(database=None, dxf=None, punticsv=None):
    """ execute db 2 dxf etl """

    # if len(args.database) >1:
    if database is None:
        database = openFileDialog(
            extensions="file databse |*.mdb;*.accdb", filename=module_path(),
            msg="Aprire Database Access")
    if database is None:
        return
    default = os.path.dirname(database)
    if punticsv is None:
        punticsv = openFileDialog(
            "file punti |*.csv", filename=default, msg="File punti csv")
    if punticsv is None:
        return

    if dxf is None:
        dxf = openFileDialog(
            "file dxf |*.dxf", filename=default, msg="Eventuale dxf")

    op = MdbOperation(database=database)
    op.silent = False
    op.echo = True
    if dxf is not None:
        op.get_lines(dxf)
    op.filesql(module_relative_file('sql', 'drop.sql')[0])
    op.filesql(module_relative_file('sql', 'create.sql')[0])
    op.filecsv(punticsv)
    op.filesql(module_relative_file('sql', 'elabs.sql')[0])
    op.initdxf()
    op.query_pozzi()
    op.query_tubi()
    op.query_condotte()
    op.query_shp_condotte()
    op.query_shp_pozzi()
    op.filesql(module_relative_file('sql', 'postelabs.sql')[0])
    op.finito()


def main():
    """ main """

    parser = argparse.ArgumentParser(description='Etl elabora file madb.')
    parser.add_argument('-database', nargs=1, required=False,
                        type=testfile, help='database')
    parser.add_argument('-dxf', nargs=1, required=False,
                        type=testfile, help='Dxf')
    parser.add_argument('-punticsv', nargs=1, required=False,
                        type=testfile, help='file punt csv')

    args = parser.parse_args()
    db = None
    csv = None
    dxf = None
    if args.database:
        db = args.database[0]
    if args.punticsv:
        csv = args.punticsv[0]
    if args.dxf:
        dxf = args.dxf[0]

    execute_dxf2shp(dxf=dxf)
    # execute_db2dxf(database=db, punticsv=csv, dxf=dxf)


def setcfg(config):
    cfg = config.get("dxf2shp", {}).get("shp_archi", None)
    if cfg:
        ShpDefinition._shp_archi = cfg
    cfg = config.get("dxf2shp", {}).get("shp_nodi", None)
    if cfg:
        ShpDefinition._shp_nodi = cfg
    cfg = config.get("dxf2shp", {}).get("dxf_archi", None)
    if cfg:
        DxfOperation._dxf_archi = cfg
    cfg = config.get("dxf2shp", {}).get("dxf_nodi", None)
    if cfg:
        DxfOperation._dxf_nodi = cfg


if __name__ == "__main__":
    # test()
    main()
