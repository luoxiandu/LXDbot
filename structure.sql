CREATE TABLE [account](
  [QQ] TEXT PRIMARY KEY NOT NULL, 
  [balance] integer NOT NULL, 
  [donate] integer NOT NULL, 
  [password] TEXT, 
  [sessionkey] TEXT, 
  [banned] INTEGER NOT NULL DEFAULT 0);

CREATE TABLE [advertisements](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
  [url] TEXT NOT NULL);

CREATE TABLE [AlipayOrders](
  [tradeNo] TEXT NOT NULL UNIQUE, 
  [amount] INTEGER NOT NULL, 
  [memo] TEXT, 
  [used] INTEGER);

CREATE TABLE [Bankstatement](
  [amount] INTEGER NOT NULL, 
  [memo] TEXT NOT NULL, 
  [time] INTEGER NOT NULL);

CREATE TABLE [beggars](
  [HWID] TEXT NOT NULL UNIQUE, 
  [IP] TEXT, 
  [lastlogin] integer, 
  [logincount] INTEGER DEFAULT 0, 
  [banned] INTEGER NOT NULL DEFAULT 0);

CREATE TABLE [cheats](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
  [dll] TEXT, 
  [xpr] TEXT, 
  [resource] TEXT, 
  [keyfile] TEXT, 
  [name] TEXT, 
  [memo] TEXT, 
  [level] INTEGER NOT NULL DEFAULT 0);

CREATE TABLE "coupon" (
  "id" TEXT NOT NULL,
  "password" TEXT,
  "used" integer,
  PRIMARY KEY ("id")
);

CREATE TABLE [ForthPartyOrders](
  [id] TEXT NOT NULL UNIQUE, 
  [amount] INTEGER NOT NULL, 
  [recieve_account_name] TEXT, 
  [orderuid] INTEGER NOT NULL);

CREATE TABLE [gamepass](
  [id] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
  [email] TEXT NOT NULL, 
  [emailpassword] TEXT NOT NULL, 
  [steam] TEXT NOT NULL DEFAULT 请自行注册, 
  [steampassword] TEXT NOT NULL DEFAULT 请自行注册, 
  [sold] integer NOT NULL DEFAULT 0, 
  [key] TEXT NOT NULL);

CREATE TABLE GameServiceOrders
(
    QQ         TEXT,
    megalodon  integer,
    whale      integer,
    greatwhite integer,
    bullshark  integer,
    tigershark integer,
    redshark   integer,
    level      text,
    unlock     text,
    paid       integer,
    finished   integer,
    total      integer
);

CREATE TABLE [injection_statistics](
  [account] text, 
  [logincount] int NOT NULL DEFAULT 0, 
  [injectcount] int NOT NULL DEFAULT 0, 
  [logincountday] int NOT NULL DEFAULT 0, 
  [injectcountday] int NOT NULL DEFAULT 0);

CREATE TABLE passkeys
(
    passkey      TEXT not null,
    HWID         text,
    inittime     integer,
    outdatedtime integer,
    duration     integer
);

CREATE TABLE [prices](
  [name] TEXT UNIQUE, 
  [price] INTEGER);

CREATE TABLE "vars" (
  "k" text NOT NULL,
  "value" TEXT,
  PRIMARY KEY ("k")
);

CREATE UNIQUE INDEX passkeys_passkey_uindex
    on passkeys (passkey);

