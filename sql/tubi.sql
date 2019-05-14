SELECT 
 X,
 Y,
 X1,
 Y1,
 OBJECTID & '-' &  SEQ & '-e' as "OBJ_ID",
 ISTAT_ID as "ISTAT_ID",
 CODE as "CODE",
 IDPUNTINI as "IDPUNINI",
 IDPUNTFIN as "IDPUNFIN",
 '' as "IDLININI",
 MATLIN as "MATLIN",
 FORMSEZ as "FORSEZ",
 ALT_LIN as "ALT_LIN",
 LARGH_LIN as "LARG_LIN",
 Z  as "QUOINI",
 QUOFIN as "QUOFIN",
 (Z - (DISLINI/100)) as "DISLINI",
 (Z - (DISFIN/100)) as "DISLFIN",
 TIPFOG as "TIPFOG",
 TIPLINIDR as "TIPLINIDR",
 POS_TRATTA as "POS_TRATTA",
 POS_SUP as "POS_SUP",
 FOTOINT as "IMAGE",
 DATA as "DATA",
 TNOTE as "NOTE",
 TLUNG as "LUNG",
 PENDENZA as "PENDENZA",
 DEN_TRONCO as "DEN_TRONC",
 SEQ,
 ENTRA,
 ESCE,
 DAPOZZO,
 VERSOPOZZO
 FROM TUBI
 where ENTRA;

SELECT 
 X,
 Y,
 X1,
 Y1,
 OBJECTID & '-' &  SEQ & '-u' as "OBJ_ID",
 ISTAT_ID as "ISTAT_ID",
 CODE as "CODE",
 IDPUNTINI as "IDPUNINI",
 IDPUNTFIN as "IDPUNFIN",
 '' as "IDLININI",
 MATLIN as "MATLIN",
 FORMSEZ as "FORSEZ",
 ALT_LIN as "ALT_LIN",
 LARGH_LIN as "LARG_LIN",
 Z  as "QUOINI",
 QUOFIN as "QUOFIN",
 (Z - (DISLINI/100)) as "DISLINI",
 (Z - (DISFIN/100)) as "DISLFIN",
 TIPFOG as "TIPFOG",
 TIPLINIDR as "TIPLINIDR",
 POS_TRATTA as "POS_TRATTA",
 POS_SUP as "POS_SUP",
 FOTOINT as "IMAGE",
 DATA as "DATA",
 TNOTE as "NOTE",
 TLUNG as "LUNG",
 PENDENZA as "PENDENZA",
 DEN_TRONCO as "DEN_TRONC",
 SEQ,
 ENTRA,
 ESCE,
 DAPOZZO,
 VERSOPOZZO
 FROM TUBI
 where ESCE;


