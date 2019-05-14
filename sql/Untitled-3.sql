SELECT 
 INI.X AS "X",
 INI.Y AS Y ","
 FIN.X AS "X1",
 FIN.Y AS "Y1",
 INI.OBJECTID & '-' & FIN.OBJECTID AS "OBJ_ID",
 INI.ISTAT_ID as "ISTAT_ID",
 INI.CODE as "CODE",
 INI.OBJECTID  as "IDPUNINI",
 FIN.OBJECTID as "IDPUNFIN",
 '' as "IDLININI",
 NZ(INI.MATLIN , FIN.MATLIN )as "MATLIN",
 NZ(INI.FORMSEZ, FIN.FORMSEZ) as "FORSEZ",
 NZ(INI.ALT_LIN, FIN.ALT_LIN) as "ALT_LIN",
 NZ(INI.LARGH_LIN, FIN.LARGH_LIN) as "LARG_LIN",
 (INI.Z - (INI.DISLINI / 100)) as "QUOINI",
 (INI.Z - (INI.DISLINI / 100)) as "QUOFIN",
 INI.DISLINI as "DISLINI",
 FIN.DISFIN as "DISLFIN",
 NZ(INI.TIPFOG, FIN.TIPFOG) as "TIPFOG",
 NZ(INI.TIPLINIDR, FIN.TIPLINIDR) as "TIPLINIDR",
 NZ(INI.POS_TRATTA, FIN.POS_TRATTA) as "POS_TRATTA",
 NZ(INI.POS_SUP, FIN.POS_SUP) as "POS_SUP",
 NZ(INI.FOTOINT, FIN.FOTOINT) as "IMAGE",
 INI.[DATA] as "DATA",
 NZ(INI.TNOTE, FIN.TNOTE) as "NOTE",
 NZ(INI.TLUNG, FIN.TLUNG) as "LUNG",
 NZ(INI.PENDENZA, FIN.PENDENZA) as "PENDENZA",
 NZ(INI.DEN_TRONCO, FIN.DEN_TRONCO) as "DEN_TRONC"
FROM (((TUBI AS INI) 
 	INNER JOIN TUBI_REL AS SE ON SE.`INI` = INI.`ID`)
 	INNER JOIN  TUBI AS FIN ON  SE.`FIN` = FIN.`ID` )
; 




SELECT 
 INI.X AS "X",
 INI.Y AS "Y",
 FIN.X AS "X1",
 FIN.Y AS "Y1",
 INI.OBJECTID & '-' & FIN.OBJECTID AS "OBJ_ID",
 INI.ISTAT_ID as "ISTAT_ID",
 INI.CODE as "CODE",
 INI.OBJECTID  as "IDPUNINI",
 FIN.OBJECTID as "IDPUNFIN",
 '' as "IDLININI",
 IIF(ISNULL(INI.MATLIN) , FIN.MATLIN ,INI.MATLIN) as "MATLIN",
 IIF(ISNULL(INI.FORMSEZ), FIN.FORMSEZ, INI.FORMSEZ) as "FORSEZ",
 IIF(ISNULL(INI.ALT_LIN), FIN.ALT_LIN, INI.ALT_LIN) as "ALT_LIN",
 IIF(ISNULL(INI.LARGH_LIN), FIN.LARGH_LIN) as "LARG_LIN",
 (INI.Z - (INI.DISLINI / 100)) as "QUOINI",
 (INI.Z - (INI.DISLINI / 100)) as "QUOFIN",
 INI.DISLINI as "DISLINI",
 FIN.DISFIN as "DISLFIN",
 IIF(ISNULL(INI.TIPFOG), FIN.TIPFOG, INI.TIPFOG) as "TIPFOG",
 IIF(ISNULL(INI.TIPLINIDR), FIN.TIPLINIDR, INI.TIPLINIDR) as "TIPLINIDR",
 IIF(ISNULL(INI.POS_TRATTA), FIN.POS_TRATTA, INI.POS_TRATTA) as "POS_TRATTA",
 IIF(ISNULL(INI.POS_SUP), FIN.POS_SUP, INI.POS_SUP) as "POS_SUP",
 IIF(ISNULL(INI.FOTOINT), FIN.FOTOINT, INI.FOTOINT) as "IMAGE",
 INI.[DATA] as "DATA",
 IIF(ISNULL(INI.TNOTE), FIN.TNOTE, INII.TNOTE) as "NOTE",
 IIF(ISNULL(INI.TLUNG), FIN.TLUNG, INII.TLUNG) as "LUNG",
 IIF(ISNULL(INI.PENDENZA), FIN.PENDENZA, INII.PENDENZA) as "PENDENZA",
 IIF(ISNULL(INI.DEN_TRONCO), FIN.DEN_TRONCO, INII.DEN_TRONCO) as "DEN_TRONC"
FROM (((TUBI AS INI) 
 	INNER JOIN TUBI_REL AS SE ON SE.`INI` = INI.`ID`)
 	INNER JOIN  TUBI AS FIN ON  SE.`FIN` = FIN.`ID` )
; 