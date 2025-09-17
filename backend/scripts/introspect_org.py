import pyodbc
cn=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=EventTrackerDB_Dev;Trusted_Connection=yes;', autocommit=True)
cur=cn.cursor()
cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='Organization'")
cols=[r[0] for r in cur.fetchall()]
print('Organization cols:', cols)
if cols:
    try:
        cur.execute('SELECT TOP 1 * FROM Organization')
        print('Sample org row:', cur.fetchone())
    except Exception as e:
        print('Select org row error:', e)
