import sqlite3
import time
import datetime
import random
from nonebot.log import logger

class DB:
    conn = None
    __VIPs__ = {}
    __beggars__ = {}
    __online__ = {}

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

    def varpp(self, key):
        cur = self.conn.cursor()
        cur.execute("UPDATE vars SET value=value+1 WHERE k=?", (key,))
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

    def getDLLList(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,memo FROM cheats")
        r = cur.fetchall()
        ret = []
        for row in r:
            ret.append({
                'id': row[0],
                'name': row[1],
                'memo': row[2]
            })
        ret.reverse()
        return ret

    def getDLL(self, id):
        cur = self.conn.cursor()
        cur.execute("SELECT dll,xpr FROM cheats WHERE id=?", (id,))
        r = cur.fetchone()
        return {
            'dllpath': r[0],
             'xprpath': r[1]
        }

    def checkSessionkey(self, sessionkey):
        # cur = self.conn.cursor()
        parts = sessionkey.split("::")
        acc = parts[0]
        sskey = parts[1]
        if acc.isdigit():
            # cur.execute("SELECT sessionkey FROM account WHERE QQ=?", (acc,))
            return DB.__VIPs__.get(acc) == sskey
        else:
            # cur.execute("SELECT sessionkey FROM beggars WHERE HWID=?", (acc,))
            return DB.__beggars__.get(acc) == sskey
        # r = cur.fetchone()
        # if r and r[0] == sskey:

    def newSessionkey(self, acc):
        # cur = self.conn.cursor()
        sessionkey = ''.join(random.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", random.randint(15, 20)))
        if acc.isdigit():
            # cur.execute("UPDATE account SET sessionkey=? WHERE QQ=?", (sessionkey, acc))
            DB.__VIPs__[acc] = sessionkey
        else:
            # cur.execute("UPDATE beggars SET sessionkey=? WHERE HWID=?", (sessionkey, acc))
            DB.__beggars__[acc] = sessionkey
        # self.conn.commit()
        return acc + '::' + sessionkey

    def clearSessionkey(self, acc):
        # cur = self.conn.cursor()
        if acc.isdigit():
            # cur.execute("UPDATE account SET sessionkey='' WHERE QQ=?", (acc,))
            del DB.__VIPs__[acc]
        else:
            # cur.execute("UPDATE beggars SET sessionkey='' WHERE HWID=?", (acc,))
            del DB.__beggars__[acc]
        # self.conn.commit()
        del DB.__online__[acc]
        return

    def newtrial(self, HWID, IP):
        cur = self.conn.cursor()
        logincount = 1
        cur.execute("SELECT logincount FROM beggars WHERE HWID=?", (HWID,))
        r = cur.fetchone()
        if r:
            logincount = r[0] + 1
        cur.execute("REPLACE INTO beggars(HWID, IP, lastlogin, logincount) VALUES (?, ?, ?, ?)", (HWID, IP, time.time(), logincount))
        self.conn.commit()
        return

    def chktrialonce(self, HWID):
        cur = self.conn.cursor()
        cur.execute("SELECT lastlogin FROM beggars WHERE HWID=?", (HWID,))
        r = cur.fetchone()
        if r:
            lastlogin = datetime.datetime.fromtimestamp(r[0])
            if datetime.datetime.now().date() != lastlogin.date():
                return True
            else:
                return False
        else:
            return True

    def onlinecount(self, HWID):
        return HWID in DB.__beggars__

    def chkonline(self):
        newonline = {}
        for acc in DB.__online__.keys():
            if DB.__online__[acc] == DB.__beggars__.get(acc) or DB.__online__[acc] == DB.__VIPs__.get(acc):
                logger.info('用户' + acc + '主动离线')
                if acc.isdigit():
                    del DB.__VIPs__[acc]
                else:
                    del DB.__beggars__[acc]
            else:
                newonline[acc] = DB.__online__[acc]
        DB.__online__ = newonline
        for acc in DB.__VIPs__.keys():
            DB.__online__[acc] = DB.__VIPs__[acc]
        for HWID in DB.__beggars__.keys():
            DB.__online__[HWID] = DB.__beggars__[HWID]

    def getonline(self):
        # cur = self.conn.cursor()
        # cur.execute("SELECT count(*) FROM beggars WHERE sessionkey != ''")
        # return cur.fetchone()[0]
        return len(DB.__online__)

    def getonlinedetail(self):
        return list(DB.__online__.keys())

    def kickonline(self, acc):
        # noinspection PyBroadException
        try:
            if acc.isdigit():
                del DB.__VIPs__[acc]
            else:
                del DB.__beggars__[acc]
            del DB.__online__[acc]
            return True
        except Exception:
            return False

    def chkpassword(self, acc, pwd):
        cur = self.conn.cursor()
        cur.execute("SELECT password FROM account WHERE QQ=?", (acc,))
        r = cur.fetchone()
        if r:
            if pwd == r[0]:
                return True
            else:
                return False
        else:
            return False

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

    def deleteaccount(self, acc):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM account WHERE QQ=?", (acc,))
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
        r = cur.execute("SELECT ROWID, amount, memo, time FROM Bankstatement WHERE time BETWEEN ? AND ?", (start, end))
        banks = r.fetchall()
        total_amount = 0
        details = []
        for line in banks:
            total_amount += line[1]
            details.append({
                'rowid': repr(line[0]),
                'amount': repr(float(line[1]) / 100),
                'memo': line[2],
                'time': time.ctime(line[3])
            })
        return {
            'total_amount': total_amount,
            'details': details
        }

    def orderGameAccountService(self, acc, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, total):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO GameServiceOrders(QQ, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, paid, finished, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            acc, megalodon, whale, greatwhite, bullshark, tigershark, redshark, level, unlock, 1, 0, total
        ))
        self.conn.commit()
        return




