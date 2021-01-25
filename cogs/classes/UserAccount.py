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
        elif type == "subtract":
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
