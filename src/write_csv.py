import sqlite3


def create():
    con = sqlite3.connect('./cache/dev.db')
    c = con.cursor()
    create_table = '''CREATE TABLE INFO
       (ID INT PRIMARY KEY     NOT NULL,
       ACCOUNT           CHAR(50),
       PASSWORD            CHAR(50),
       DEVICE       CHAR(50),
       FMS       CHAR(50),
       MESSAGE       CHAR(50),
       LIST         INT);'''
    c.execute(create_table)
    con.commit()
    con.close()


def insert(sql_):
    con = sqlite3.connect('./cache/dev.db')
    c = con.cursor()
    c.execute(sql_)
    con.commit()
    con.close()


def query(sql_):
    con = sqlite3.connect('./cache/dev.db')
    c = con.cursor()
    cursor = c.execute(sql_).fetchall()
    con.close()
    return cursor


def update(sql_):
    con = sqlite3.connect('./cache/dev.db')
    c = con.cursor()
    c.execute(sql_)
    con.commit()
    con.close()
