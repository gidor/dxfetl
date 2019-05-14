"""command line interface per trasformazioni Geocomp"""
import os
from cement import ex, Controller, App, init_defaults
import yaml
from etl import execute_db2dxf, execute_dxf2shp
from monografie import execute_monografia
from helpers import testfile, test_dir, module_path, module_relative_file


class MyBaseController(Controller):
    """ solo una root
    """
    class Meta:
        "Meta"
        label = 'base'
        description = "Cli"


class EtlController(Controller):
    """ import planimetrie"""
    class Meta:
        label = 'items'
        stacked_type = 'embedded'
        stacked_on = 'base'
        # config_defaults = dict(outdir=os.path.join(module_path(), 'out'))

    def show(self):
        print("self.app.pargs")
        print(self.app.pargs)

    @ex(help="importa dataset data set  di impianto ",
        arguments=[
            (["-database", ],
             {
                "action": "store",
                "help": "database access",
                "nargs": 1,
                "dest": 'database',
                "type": str,
                "required": False,
            }),
            (["-punticsv", ],
             {
                "action": "store",
                "help": "punti csv",
                "nargs": 1,
                "dest": 'punticsv',
                "type": testfile,
                "required": False,
            }),
            (["-dxf", ],
             {
                "action": "store",
                "help": "dxf per geometrie condotte",
                "nargs": 1,
                "dest": 'dxf',
                "type": testfile,
                "required": False,
            }),
        ]
        )
    def etl(self):
        "etl "
        database = self.app.pargs.database
        punticsv = self.app.pargs.punticsv
        dxf = self.app.pargs.dxf
        execute_db2dxf(database=database, punticsv=punticsv, dxf=dxf)

    @ex(help="crea shp da dxf",
        arguments=[
            (["-dxf", ],
             {
                "action": "store",
                "help": "dxf per geometrie condotte",
                "nargs": 1,
                "dest": "dxf",
                "type": testfile,
                "required": False,
            }),
        ]
        )
    def dxftoshp(self):
        "dxf 2 shp"

        dxf = self.app.pargs.dxf
        if isinstance(dxf, list):
            execute_dxf2shp(dxf=dxf[0])
        else:
            execute_dxf2shp(dxf=None)

    @ex(help="crea monografia",
        arguments=[
            (["-database", ],
             {
                "action": "store",
                "help": "database Access",
                "nargs": 1,
                "dest": "database",
                "type": testfile,
                "required": False,
            }),
            (["-filtro", ],
             {
                "action": "store",
                "help": "filtro pu essere BIANCA NERA ALL o un numero di scheda",
                "nargs": 1,
                "dest": "filtro",
                "type": str,
                "required": False,
            }),
        ]
        )
    def monografia(self):
        "creazione monografie"
        dbfile = self.app.pargs.database
        dbfiltro = self.app.pargs.fltro
        execute_monografia(database=dbfile, filtro=dbfiltro)


defaults = init_defaults('etl')
cfgfile, exist = module_relative_file('sql', 'config.yaml')
if exist:
    cfg = yaml.load(open(cfgfile))
else:
    cfg = {}

defaults = {'etl': cfg}


class EtlApp(App):
    "l'applicazione"

    class Meta:
        "meta"
        label = "cli"
        # config_defaults = DEFAULTS
        base_controller = 'base'
        # extensions = ['ext_json', 'ext_tabulate']
        # output_handler = 'ext_tabulate'
        config_defaults = defaults

        handlers = [
            MyBaseController,
            EtlController,
            # MonografiaController,
        ]


with EtlApp() as app:
    app.run()
    # print("Foo => %s" % app.config.get('etl', 'foo'))
