from .classes.UserAccount import UserAccount
from discord.utils import get
import json
import asyncio
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class GlobalFunctions:
    def __init__(self):
        return

    def check_block(id, command):
        print("id: {} Command: {}".format(id, command))
        user = UserAccount(int(id))

        for blocked_command in user.blocked_commands():
            print(blocked_command[0])
            if command == blocked_command[0]:
                return False
        else:
            return True

    def get_value(key):
        with open("C:/Users/frogg/Desktop/Arnold/cogs/hidden.json") as f:
            return json.load(f)[key]

    async def get_id(guild, type):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT type_id FROM command_check WHERE server_id=? and type=?", (guild.id, type,))
        try:
            type_id = c.fetchone()[0]
            print(type_id)
            return type_id
        except:
            default = get(guild.roles, name="@everyone")
            perms = default.permissions
            perms.update(send_messages=False)
            role = await guild.create_role(name=type, permissions=perms)


            c.execute("INSERT INTO command_check (type_id, server_id, type) VALUES (?,?,?)", (role.id, guild.id, type,))
            conn.commit()
            conn.close()

            return role.id
