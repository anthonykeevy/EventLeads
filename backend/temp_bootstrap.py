import sqlite3, os
BASE = os.path.dirname(__file__) or '.'
DB_PATH = os.path.join(BASE, 'temp_migrate.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
sqls = [
    "CREATE TABLE IF NOT EXISTS Organization (OrganizationID INTEGER PRIMARY KEY, Name TEXT)",
    "CREATE TABLE IF NOT EXISTS Event (EventID INTEGER PRIMARY KEY, OrganizationID INTEGER, StartDate DATE, DurationDays INTEGER)",
    "CREATE TABLE IF NOT EXISTS CanvasLayout (CanvasLayoutID INTEGER PRIMARY KEY, EventID INTEGER)",
    "CREATE TABLE IF NOT EXISTS CanvasObject (CanvasObjectID INTEGER PRIMARY KEY)",
    "CREATE TABLE IF NOT EXISTS Lead (LeadID INTEGER PRIMARY KEY, EventID INTEGER, SubmittedAt DATETIME)",
    "CREATE TABLE IF NOT EXISTS Invoice (InvoiceID INTEGER PRIMARY KEY)",
    "CREATE TABLE IF NOT EXISTS ObjectType (ObjectTypeID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Category TEXT, IsSystemDefault INTEGER)",
    "CREATE TABLE IF NOT EXISTS User (UserID INTEGER PRIMARY KEY)"
]
for s in sqls:
    c.execute(s)
conn.commit()
print('created temp db at', DB_PATH)
