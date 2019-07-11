import sqlite3

conn = sqlite3.connect('database.db')

c = conn.cursor()

# c.execute('''CREATE TABLE monitoring (
# 			url text,
# 			status integer,
# 			speed float
# 			)''')

conn.commit()

conn.close()

