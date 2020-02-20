import sqlite3

def table():
   
    query = """CREATE TABLE "crypto" (
	    "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	    "date"	INTEGER NOT NULL,
	    "time"	TEXT NOT NULL,
	    "from_currency"	INTEGER NOT NULL,
	    "from_quantity"	REAL NOT NULL,
	    "to_currency"	INTEGER NOT NULL,
	    "to_quantity"	REAL NOT NULL,
	    "P.U"	INTEGER NOT NULL ) """

    conn = sqlite3.connect('./data/base_date.db')
    c = conn.cursor()
    c.execute(query)

if __name__ == '__main__':
    table()

