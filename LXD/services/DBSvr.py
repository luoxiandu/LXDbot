import sqlite3

class DB:
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect("data/LXD.db")

    def __del__(self):
        self.conn.close()

    def getvar(self, key):
        cur = self.conn.cursor()
        r = cur.execute("SELECT value FROM vars WHERE k=?", (key,))
        val = r.fetchone()
        return val[0] if val else None

    def setvar(self, key, val):
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO vars VALUES (?, ?)", (key, val))
        self.conn.commit()
        return

    def addgamepass(self, gamepassList):
        cur = self.conn.cursor()
        for gp in gamepassList:
            cur.execute("INSERT INTO gamepass(email, emailpassword, steam, steampassword, sold) VALUES (?, ?, ?, ?, 0)", (
                gp['email'],
                gp['emailpassword'],
                gp['steam'],
                gp['steampassword']
            ))
        self.conn.commit()
        return

    def getgamepass(self):
        cur = self.conn.cursor()
        r = cur.execute("SELECT * FROM gamepass WHERE sold=0 LIMIT 1")
        gp = r.fetchone()
        gp = {
            'id': gp[0],
            'email': gp[1],
            'emailpassword': gp[2],
            'steam': gp[3],
            'steampassword': gp[4]
        }
        cur.execute("UPDATE gamepass SET sold=1 WHERE id=?", (gp['id'],))
        self.conn.commit()
        return gp

    # amo以分为单位的整数，切记切记
    def deposit(self, acc, amo):
        cur = self.conn.cursor()
        r = cur.execute("SELECT balance FROM account WHERE QQ=?", (acc,))
        balance = r.fetchone()
        if not balance:
            cur.execute("INSERT INTO account(QQ, balance, donate) VALUES (?, ?, ?)", (acc, amo, 0))
            self.conn.commit()
            return
        else:
            balance = balance[0]
            balance += amo
            cur.execute("UPDATE account SET balance=? WHERE QQ=?", (balance, acc))
            self.conn.commit()
            return

    def cost(self, acc, amo):
        cur = self.conn.cursor()


