import sqlite3
import time

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
            cur.execute("INSERT INTO gamepass(email, emailpassword, steam, steampassword, sold, key) VALUES (?, ?, ?, ?, 0, ?)", (
                gp['email'],
                gp['emailpassword'],
                gp['steam'],
                gp['steampassword'],
                gp['key'],
            ))
        self.conn.commit()
        return

    def getgamepass(self):
        cur = self.conn.cursor()
        r = cur.execute("SELECT id, email, emailpassword, steam, steampassword, key FROM gamepass WHERE sold=0 LIMIT 1")
        gp = r.fetchone()
        if not gp:
            return None
        else:
            gp = {
                'id': gp[0],
                'email': gp[1],
                'emailpassword': gp[2],
                'steam': gp[3],
                'steampassword': gp[4],
                'key': gp[5],
            }
            cur.execute("UPDATE gamepass SET sold=1 WHERE id=?", (gp['id'],))
            self.conn.commit()
            return gp

    def checkgamepass(self):
        cur = self.conn.cursor()
        r = cur.execute("SELECT count(*) FROM gamepass WHERE sold=0")
        gpamount = r.fetchone()
        return gpamount[0]

    def setpassword(self, acc, pwd):
        cur = self.conn.cursor()
        r = cur.execute("SELECT balance FROM account WHERE QQ=?", (acc,))
        balance = r.fetchone()
        if not balance:
            cur.execute("INSERT INTO account(QQ, balance, donate, password) VALUES (?, ?, ?, ?)", (acc, 0, 0, pwd))
            self.conn.commit()
            return
        else:
            cur.execute("UPDATE account SET password=? WHERE QQ=?", (pwd, acc))
            self.conn.commit()
            return

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
                'used': bool(trade[3])
            }

    def useAlipayTradeNo(self, tradeNo):
        cur = self.conn.cursor()
        cur.execute("UPDATE AlipayOrders SET used=1 WHERE tradeNo=?", (tradeNo,))
        self.conn.commit()
        return

    def getRandomAlipayTradeNo(self):
        cur = self.conn.cursor()
        r = cur.execute("SELECT * FROM AlipayOrders ORDER BY RANDOM() LIMIT 1")
        trade = r.fetchone()
        if not trade:
            return None
        else:
            return trade[0]

    def saveForthPartyOrder(self, order):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO ForthPartyOrders(id, amount, recieve_account_name, orderuid)  VALUES (?, ?, ?, ?)", (
            order['orderid'],
            order['price'],
            order['account_name'],
            order['orderuid']
        ))
        self.conn.commit()
        return

    def saveStatement(self, amo, memo):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Bankstatement(amount, memo, time) VALUES (?, ?, ?)", (amo, memo, time.time()))
        self.conn.commit()
        return

    def getStatementByInterval(self, start, end):
        cur = self.conn.cursor()
        r = cur.execute("SELECT ROWID, amount, memo FROM Bankstatement WHERE time BETWEEN ? AND ?", (start, end))
        banks = r.fetchall()
        total_amount = 0
        details = []
        for line in banks:
            total_amount += line[1]
            details.append({
                'rowid': repr(line[0]),
                'amount': repr(float(line[1]) / 100),
                'memo': line[2]
            })
        return {
            'total_amount': total_amount,
            'details': details
        }




