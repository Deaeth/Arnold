import os
import sqlite3
import asyncio
import time
import random

BASE_DIR = "C:/Users/frogg/Desktop/Arnold/cogs"
db_path = os.path.join(BASE_DIR, "db.db")

class UserAccount:
    def __init__(self, id):
        self.id = id

    def change_money(self, amount, type):
        sql = ""
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if type == "add":
            sql = "UPDATE users SET balance = balance + ? WHERE user_id=?"
        elif type == "remove":
            sql = "UPDATE users SET balance = balance - ? WHERE user_id=?"
        else:
            return

        c.execute(sql, (amount, self.id,))
        conn.commit()

        return True

    def get_balance(self):
        sql = "SELECT balance FROM users WHERE user_id=?"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(sql, (self.id,))
        balance = c.fetchone()[0]
        print(balance)
        conn.close()
        return balance

    def change_stock(self, ticker, amount, type):
        sql = ""
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM portfolio WHERE user_id=? AND ticker=?", (self.id, ticker,))
        row = c.fetchone()

        if row:
            if type == "buy":
                c.execute("UPDATE portfolio SET shares=shares+? WHERE user_id=? AND ticker=?", (amount, self.id, ticker,))
            elif type == "sell":
                c.execute("UPDATE portfolio SET shares=shares-? WHERE user_id=? AND ticker=?", (amount, self.id, ticker,))
                conn.commit()
                shares = self.get_stock(ticker)
                print(shares)
                if shares == 0:
                    c.execute("DELETE FROM portfolio WHERE user_id=? AND ticker=?", (self.id, ticker,))

            conn.commit()
            conn.close()
            return
        if type == "buy":
            c.execute("INSERT INTO portfolio (ticker, shares, user_id) VALUES (?,?,?)", (ticker, amount, self.id,))
            conn.commit()
            return
        return "You do not own that stock"

    def get_stock(self, ticker):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT shares FROM portfolio WHERE user_id=? and ticker=?", (self.id, ticker,))
        shares = c.fetchone()[0]

        return shares


    def get_portfolio(self, page=None):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if page == None:
            c.execute("SELECT ticker, shares FROM portfolio WHERE user_id=? ORDER BY id ASC LIMIT 5", (self.id,))
            stocks = c.fetchall()
            return stocks

        index = (page-1)*5
        print(index)

        c.execute("SELECT ticker, shares FROM portfolio WHERE user_id=? ORDER BY id ASC LIMIT 5 OFFSET ?", (self.id, index,))
        stocks = c.fetchall()

        return stocks




    def add_points(self, amount):
        sql = "UPDATE users SET score = score + ? WHERE user_id=?"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(sql, (round(amount), self.id,))
        conn.commit()
        conn.close()

    def add_pomodoro(self, amount):
        sql = "UPDATE users SET pomodoro = pomodoro + ? WHERE user_id=?"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(sql, (amount, self.id,))
        conn.commit()
        conn.close()

    def blocked_commands(self):
        sql = "SELECT command FROM blocked WHERE user_id=?"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(sql, (self.id,))
        rows = c.fetchall()
        conn.close()

        return rows
