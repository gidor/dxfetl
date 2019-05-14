# manuale etl_dist

la distribuzione contiene un eseguibile cli.exe e due comandi bat etl.bat e dxfshp.bat.

## etl.bat 

Permette di generare i file dxf da un database access.

Dopo il lancio apre una finestra di navigazione del disco che chiede il file database, quindi chiede eventuale dxf da cui estrae le geometrie delle condotte.

Il dxf serve a modificare le  condotto qualora non siano lineari da pozzetto a pozzetto.

Il comando genera un dxf  e shape file nella stessa direcotory del database.

## dxfshp.bat

Generare gli shape file da un file dxf.

Dopo il lancio apre una finestra di navigazione del disco che chiede il file dxf.

Il comando genera shape file nella stessa direcotory del dxf.

## configurazione

il file di configurazione è nella directory cli e può essere scritta come json "config.json" o coma yaml "config.yaml".
nella distribuzione è presente il file config.yaml perchè generalmente più facile da leggere e da scrivere.

La confgurazione è una gerarchia di informazioni che descrivono gli shapefile il dxf e le loro dipendenze reciproche


- dxf2shp.shp_archi.defs contiene la descrizione dei campi dello shape archi.
- dxf2shp.shp_archi.name è il nome  dello shape archi.
- dxf2shp.shp_nodi.defs contiene la descrizione dei campi dello shape nodi.
- dxf2shp.shp_nodi.name  è il nome dello shape nodi.
- dxf2shp.dxf_archi.layers è la lista di layers in cui cercare gli archi.
- dxf2shp.dxf_archi.atts è la lista dei tag degli attributi per gli archi.
- dxf2shp.dxf_archi.element è la tipologia di elementi grafico da cercare per gli archi.
- dxf2shp.dxf_archi.mapping contiene l'associazione l'attributo ed il campo dello shape per gli archi.
- dxf2shp.dxf_archi.block.layers contiene la lista dei layers dove cercare il blocco con gli attributi degli archi.
- dxf2shp.dxf_archi.block.name contiene il nome del blocco con gli attributi degli archi.

- dxf2shp.dxf_nodi.layers di.name  è la lista di layers in cui cercare gli archi.
- dxf2shp.dxf_nodi.atts è la lista dei tag degli attributi per i nodi.
- dxf2shp.dxf_nodi.element è la tipologia di elementi grafico da cercare per i nodi.
- dxf2shp.dxf_nodi.mapping contiene l'associazione l'attributo ed il campo dello shape per i nodi.


