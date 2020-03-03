import sqlite3
import sys
import os
from pathlib import Path

dbfile = os.path.join(Path(__file__).parent.absolute(), "database/Risk.db")

def auth(user, password):

    conn = sqlite3.connect(dbfile)

    c = conn.cursor()

    result = c.execute("""SELECT * FROM accounts WHERE username = '{}' and password = '{}'""".format(user, password))

    rows = result.fetchall()

    if len(rows) == 1:
        return True, (rows[0][2], rows[0][3], rows[0][4])
    else:
        return False, (0, 0, 0)

    conn.commit()

    conn.close()
