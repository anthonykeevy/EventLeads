import pyodbc

DB='EventTrackerDB_Dev'
servers=['localhost','(localdb)\\MSSQLLocalDB','localhost\\SQLEXPRESS','.' ]
cn=None
server=None
for s in servers:
    try:
        cn=pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={s};DATABASE={DB};Trusted_Connection=yes;', autocommit=True)
        server=s
        break
    except Exception as e:
        cn=None
if not cn:
    raise SystemExit('could not connect')
print('Connected to', server)
cur=cn.cursor()
for tbl in ['Role','Roles','User','UserRole']:
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", tbl)
    cols=[r[0] for r in cur.fetchall()]
    print(tbl, '=>', cols)
