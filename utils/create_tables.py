tables = '''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username VARCHAR(255) NOT NULL,
password VARCHAR(255) NOT NULL,
ter_num TEXT NOT NULL,
tg_id INTEGER(20),
region VARCHAR(255) NOT NULL,
position VARCHAR(255) NOT NULL,
grade VARCHAR(255),
points INTEGER(20),
kas VARCHAR(255) NOT NULL,
citimanager VARCHAR(255) NOT NULL,
plan_pss REAL,
fact_pss REAL,
[%_pss] REAL,
plan_osa REAL,
fact_osa REAL,
[%_osa] REAL,
plan_tt REAL,
fact_tt REAL,
[%_tt] REAL,
plan_visits REAL,
fact_visits REAL,
[%_visits] REAL,
isa_osa REAL
);
CREATE TABLE IF NOT EXISTS planograms(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR(255) NOT NULL,
cluster INTEGER(10) NOT NULL,
chain_name VARCHAR(255) NOT NULL,
shop_name VARCHAR(255) NOT NULL,
file_link VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS tt(
id INTEGER PRIMARY KEY AUTOINCREMENT,
tt_num INTEGER UNIQUE NOT NULL,
region TEXT NOT NULL,
address TEXT UNIQUE NOT NULL,
mr TEXT UNIQUE NOT NULL,
kas TEXT NOT NULL,
citimanager TEXT NOT NULL,
plan_pss REAL,
fact_pss REAL,
[%_pss] REAL,
plan_osa REAL,
fact_osa REAL,
[%_osa] REAL,
plan_tt REAL,
fact_tt REAL,
[%_tt] REAL,
plan_visits REAL,
fact_visits REAL,
[%_visits] REAL,
isa_osa REAL,
dmp_text REAL,
[%_dmp] REAL,
dmp_comm TEXT
);
CREATE TABLE best_practice(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
desc TEXT,
user_added TEXT REFERENCES users (id),
datetime_added TEXT,
datetime_start TEXT,
datetime_stop TEXT,
is_active INTEGER,
pics TEXT
);
CREATE TABLE best_practice_mr(
id INTEGER PRIMARY KEY AUTOINCREMENT,
best_practice REFERENCES best_practice (id) ON DELETE CASCADE,
user_added TEXT REFERENCES users (id) ON DELETE CASCADE,
datetime_added TEXT,
desc TEXT,
pics TEXT,
likes INTEGER,
unlikes INTEGER,
approved INTEGER,
active INTEGER
);

'''