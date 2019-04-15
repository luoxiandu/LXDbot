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

    def getprice(self, item):
        cur = self.conn.cursor()
        r = cur.execute("SELECT price FROM prices WHERE name=?", (item,))
        price = r.fetchone()[0]
        return price

    def setprice(self, item, price):
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO prices VALUES (?, ?)", (item, price))
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
        if not gp:
            return None
        else:
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

    def checkgamepass(self):
        cur = self.conn.cursor()
        r = cur.execute("SELECT count(*) FROM gamepass WHERE sold=0")
        gpamount = r.fetchone()
        return gpamount[0]

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
        r = cur.execute("SELECT balance FROM account WHERE QQ=?", (acc,))
        balance = r.fetchone()
        if not balance:
            return False
        else:
            balance = balance[0]
            if balance >= amo:
                balance -= amo
                cur.execute("UPDATE account SET balance=? WHERE QQ=?", (balance, acc))
                self.conn.commit()
                return True
            else:
                return False

    def getbalance(self, acc):
        cur = self.conn.cursor()
        r = cur.execute("SELECT balance FROM account WHERE QQ=?", (acc,))
        balance = r.fetchone()
        if not balance:
            return None
        else:
            return balance[0]

    def saveAlipayTradeNo(self, trade):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO AlipayOrders(tradeNo, amount, memo, used)  VALUES (?, ?, ?, 0)", (
            trade['tradeNo'],
            trade['amount'],
            trade['memo']
        ))
        self.conn.commit()
        return

    def getAlipayTradeNo(self, tradeNo):
        cur = self.conn.cursor()
        r = cur.execute("SELECT * FROM AlipayOrders WHERE tradeNo=?", (tradeNo,))
        trade = r.fetchone()
        if not trade:
            return None
        else:
            return {
                'tradeNo': trade[0],
                'amount': trade[1],
                'memo': trade[2],
                'used': trade[3]
            }




