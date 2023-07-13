TABLES = '''
CREATE TABLE users (
    id          INTEGER       PRIMARY KEY AUTOINCREMENT,
    username    VARCHAR (255),
    ter_num     TEXT,
    password    VARCHAR (255),
    tg_id       INTEGER (20),
    region      VARCHAR (255),
    position    VARCHAR (255),
    grade       VARCHAR (255),
    points      INTEGER (20),
    kas         VARCHAR (255),
    citimanager VARCHAR (255),
    plan_pss    REAL,
    fact_pss    REAL,
    [%_pss]     REAL,
    plan_osa    REAL,
    fact_osa    REAL,
    [%_osa]     REAL,
    plan_tt     REAL,
    fact_tt     REAL,
    [%_tt]      REAL,
    plan_visits INTEGER,
    fact_visits INTEGER,
    [%_visits]  REAL,
    isa_osa     REAL
);
CREATE TABLE tt (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tt_num      INTEGER UNIQUE,
    region      TEXT,
    chain       TEXT,
    address     TEXT,
    mr          TEXT,
    kas         TEXT,
    citimanager TEXT,
    plan_pss    REAL,
    fact_pss    REAL,
    [%_pss]     REAL,
    plan_osa    REAL,
    fact_osa    REAL,
    [%_osa]     REAL,
    plan_tt     REAL,
    fact_tt     REAL,
    [%_tt]      REAL,
    plan_visits INTEGER,
    fact_visits INTEGER,
    [%_visits]  REAL,
    isa_osa     REAL,
    dmp_text    REAL,
    [%_dmp]     REAL,
    dmp_comm    TEXT
);
CREATE TABLE promo (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_name TEXT,
    file_link TEXT
);
CREATE TABLE planograms (
    id         INTEGER       PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR (255) NOT NULL,
    cluster    INTEGER (10)  NOT NULL,
    chain_name VARCHAR (255) NOT NULL,
    shop_name  VARCHAR (255) NOT NULL,
    file_link  VARCHAR (255) NOT NULL
);
CREATE TABLE best_practice (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    region         TEXT,
    name           TEXT,
    desc           TEXT,
    user_added     TEXT,
    datetime_added TEXT,
    datetime_start TEXT,
    datetime_stop  TEXT,
    is_active      INTEGER,
    over           INTEGER,
    file_link      TEXT
);
CREATE TABLE best_practice_mr (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    best_practice  TEXT,
    username       TEXT,
    kas            TEXT,
    tg_id          INTEGER,
    datetime_added TEXT,
    desc           TEXT,
    file_link      TEXT,
    likes          INTEGER,
    unlikes        INTEGER,
    kas_checked    INTEGER,
    kas_approved   INTEGER,
    cm_checked     INTEGER,
    cm_approved    INTEGER,
    active         INTEGER,
    posted         INTEGER
);
'''