CREATE TABLE PUNTI (
	[ID] AUTOINCREMENT PRIMARY KEY,
	OBJECTID VARCHAR(20),
    X DOUBLE,
    Y DOUBLE,
    Z DOUBLE
);

CREATE TABLE TUBI (
	[ID] AUTOINCREMENT PRIMARY KEY,
	OBJECTID VARCHAR(255),
	ISTAT_ID VARCHAR(255),
	DATA TIMESTAMP,
	CODE VARCHAR(255),
	SEQ INTEGER,
	X DOUBLE,
	Y DOUBLE, 
	Z DOUBLE, 
	X1 DOUBLE,
	Y1 DOUBLE,
	QUOINI DOUBLE, 
	QUOFIN DOUBLE, 
	IDPUNTINI INTEGER,
	IDPUNTFIN INTEGER,
	ENTRA BIT,
	ESCE BIT,
	TNOTE VARCHAR(255),
	FOTOINT VARCHAR(255),
	MATLIN VARCHAR(255),
	FORMSEZ VARCHAR(255),
	TIPFOG VARCHAR(255),
	TIPLINIDR VARCHAR(255),
	POS_TRATTA VARCHAR(255),
	POS_SUP VARCHAR(255),
	DEN_TRONCO VARCHAR(255),
	DAPOZZO VARCHAR(255),
	VERSOPOZZO VARCHAR(255),
	ALT_LIN INTEGER,
	LARGH_LIN INTEGER,
	DISLINI INTEGER ,
	DISFIN INTEGER ,
	PENDENZA DOUBLE,
	TLUNG DOUBLE,
	FONTUBO DOUBLE
) ;


CREATE TABLE POZZI (
	[ID] AUTOINCREMENT PRIMARY KEY,
	OBJECTID VARCHAR(20),
	ISTAT_ID VARCHAR(8),
	X DOUBLE,
	Y DOUBLE,
	Z DOUBLE,
	QUOINFPOZ DOUBLE,
	QUOPUN DOUBLE,
	QUOTERR DOUBLE,
	QUOTRAVASO DOUBLE,
	TRAVASO INTEGER,
	SPES_SUP INTEGER,
	LARG_CHIU INTEGER,
	LUNG_CHIU INTEGER,
	LARG_SUP INTEGER,
	LUNG_SUP INTEGER,
	LARG_INF INTEGER,
	LUNG_INF INTEGER,
	COP_CHIU BIT,
	APP_CHIU BIT,
	COLPOZ BIT,
	FORMA_SUP VARCHAR(4),
	MAT_CHIU VARCHAR(4),
	MAT_SUP VARCHAR(4),
	MAT_INF VARCHAR(25),
	MAT_COLPOZ VARCHAR(2),
	FORMA_INF VARCHAR(4),
	RESPTECNI VARCHAR(255),
	CODE VARCHAR(25),
	FORM_CHIU VARCHAR(4),
	DATA TIMESTAMP,
	TNOTE VARCHAR(255),
	SUPPOSA VARCHAR(4),
	DISEGNI VARCHAR(255),
	POS_NODO VARCHAR(255),
	POS_SUP VARCHAR(255),
	DEN_PUN VARCHAR(2),
	TIMAGE VARCHAR(255),
	BLOCCO VARCHAR(255),
	LAYER VARCHAR(255),
	FOTOPOZEST VARCHAR(255),
	FOTOPOZINT VARCHAR(255)
);

create table CONDOTTE (
 ID_KEY COUNTER NOT NULL, 
 X DOUBLE,
 Y DOUBLE,
 X1 DOUBLE,
 Y1 DOUBLE,
 DH DOUBLE,
 INI_ID VARCHAR(255),
 FIN_ID VARCHAR(255),
 OBJ_ID VARCHAR(255),
 ISTAT_ID VARCHAR(255),
 CODE VARCHAR(255),
 IDPUNINI VARCHAR(255),
 IDPUNFIN VARCHAR(255),
 IDLININI VARCHAR(255),
 MATLIN    VARCHAR(255), 
 FORMSEZ   VARCHAR(255), 
 ALT_LIN   VARCHAR(255), 
 LARGH_LIN VARCHAR(255), 
 QUOINI DOUBLE ,
 QUOFIN DOUBLE ,
 DISLINI DOUBLE,
 DISLFIN DOUBLE,
 TIPFOG VARCHAR(255),
 TIPLINIDR VARCHAR(255),
 POS_TRATTA VARCHAR(255),
 POS_SUP VARCHAR(255),
 FOTOINT VARCHAR(255),
 [DATA] DATE,
 TNOTE  VARCHAR(255),
 TLUNG DOUBLE,
 PENDENZA DOUBLE,
 DEN_TRONCO VARCHAR(255),
 LAYER VARCHAR(255),
 SECONDARY VARCHAR(255), 
 MATERIALE VARCHAR(255),
 FORMA VARCHAR(255)
);


CREATE TABLE POZZI_CONDOTTE (ID_CONDOTTA INTEGER, ID_POZZO VARCHAR(255));

CREATE TABLE TUBI_REL (INI INTEGER, FIN INTEGER);

CREATE TABLE ERRORI_TUBI (ID_KEY AUTOINCREMENT PRIMARY KEY, ERRORE VARCHAR(255) ) ;


CREATE TABLE TLAYERS ( COD VARCHAR(255), VAL VARCHAR(255));

INSERT INTO TLAYERS (COD, VAL) VALUES ( '02','20_RETE-FOGNATURA-BIANCA');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '03','20_RETE-FOGNATURA-NERA');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '04','20_RETE-FOGNATURA-MISTA');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '91','20_RETE-FOGNATURA-MISTA');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '92','20_RETE-SCOLMATORE');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '93','20_RETE-METEORICHE-STRADALI');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '94','20_F-TRATTO PRIVATO');
INSERT INTO TLAYERS (COD, VAL) VALUES ( '95','20_RETE-FOSSI');


CREATE TABLE TFORSEZ ( COD VARCHAR(255), VAL VARCHAR(255));

INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '02','ø ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '03','OV ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '04','OV ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '05','OV ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '06','SC ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '07','SC ');
INSERT INTO TFORSEZ ( COD, VAL) VALUES ( '08',' ');

CREATE TABLE MONO (
P_OBJECTID VARCHAR(255), 
P_ISTAT_ID VARCHAR(255),
P_QUOINFPOZ VARCHAR(255), 
P_QUOPUN VARCHAR(255), 
P_QUOTERR VARCHAR(255), 
P_QUOTRAVASO VARCHAR(255), 
P_TRAVASO VARCHAR(255), 
P_SPES_SUP VARCHAR(255), 
P_LARG_CHIU VARCHAR(255),
P_LUNG_CHIU VARCHAR(255),
P_LARG_SUP VARCHAR(255), 
P_LUNG_SUP VARCHAR(255), 
P_LARG_INF VARCHAR(255), 
P_LUNG_INF VARCHAR(255), 
P_COP_CHIU VARCHAR(255), 
P_APP_CHIU VARCHAR(255), 
P_COLPOZ VARCHAR(255), 
p_CODE VARCHAR(255),
p_FORMA_SUP VARCHAR(255),
p_FORMA_INF VARCHAR(255),
p_FORM_CHIU VARCHAR(255),
p_MAT_CHIU VARCHAR(255), 
p_MAT_SUP VARCHAR(255),
p_MAT_INF VARCHAR(255), 
p_MAT_COLPOZ VARCHAR(255),
P_POS_NODO VARCHAR(255), 
P_POS_SUP VARCHAR(255),
P_BLOCCO VARCHAR(255), 
P_LAYER VARCHAR(255), 
P_FOTOPOZEST VARCHAR(255), 
P_FOTOPOZINT VARCHAR(255),
C_DH VARCHAR(255), 
c_INI_ID VARCHAR(255), 
c_FIN_ID VARCHAR(255),
C_OBJ_ID VARCHAR(255), 
C_ISTAT_ID VARCHAR(255), 
C_CODE VARCHAR(255), 
C_IDPUNINI VARCHAR(255), 
C_IDPUNFIN VARCHAR(255), 
C_IDLININI VARCHAR(255),  
C_ALT_LIN VARCHAR(255), 
C_LARGH_LIN VARCHAR(255), 
C_QUOINI DOUBLE, 
C_QUOFIN DOUBLE, 
C_DISLINI DOUBLE, 
C_DISLFIN DOUBLE, 
C_TIPFOG VARCHAR(255), 
C_TIPLINIDR VARCHAR(255), 
C_POS_TRATTA VARCHAR(255), 
C_POS_SUP VARCHAR(255), 
C_FOTOINT VARCHAR(255), 
C_TNOTE VARCHAR(255), 
C_TLUNG DOUBLE, 
C_PENDENZA DOUBLE, 
C_DEN_TRONCO VARCHAR(255), 
C_LAYER VARCHAR(255), 
C_SECONDARY VARCHAR(255), 
C_MATERIALE VARCHAR(255), 
C_FORMA VARCHAR(255),
C_TIPOFOGNA VARCHAR(255)
);