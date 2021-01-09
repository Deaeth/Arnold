from discord.ext import commands
import discord
import os
import sqlite3
import asyncio
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def casino(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of casino command")
            await asyncio.sleep(2)
            await msg.delete()


    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.db")

    @casino.command(pass_context=True)
    @commands.is_owner()
    async def create(self, ctx, question, option_one, option_two, timeLimit):
        origMsg = await ctx.send("**NEW CASINO BET**\n*Open for {} seconds*\n\n**QUESTION**: {}\nOption One: {}\nOption Two: {}".format(timeLimit, question, option_one, option_two))

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO casino (bet_id, status) VALUES (?,?)", (ctx.author.id,"active",))
        conn.commit()

        await asyncio.sleep(int(timeLimit))
        await origMsg.edit(content="**NEW CASINO BET**\n*Casino is closed*\n\n**QUESTION**: {}\nOption One: {}\nOption Two: {}".format(question, option_one, option_two))
        c.execute("UPDATE casino SET status=? WHERE bet_id=?", ("inactive",ctx.author.id))
        conn.commit()
        return

    @casino.command(pass_context=True)
    async def join(ctx, option, bet):
        await ctx.message.delete()
        try:
            option = int(option)
            bet = int(bet)
        except Exception:
            msg = await ctx.send("Your choice and bet must be integers")
            await asyncio.sleep(3)
            await msg.delete()
            return

        if option != 1 and option != 2:
            msg = await ctx.send("You must pick 1 or 2 for your options")
            await asyncio.sleep(3)
            await msg.delete()
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM bets WHERE user_id=?", (ctx.author.id,))
        row = c.fetchone()

        if row:
            msg = await ctx.send("You've already placed your bet!")
            await asyncio.sleep(3)
            await msg.delete()
            return

        c.execute("SELECT * FROM users WHERE user_id=?", (ctx.author.id,))
        row = c.fetchone()

        if row[2] < bet:
            msg = await ctx.send("You don't have that much to bet!")
            await asyncio.sleep(3)
            await msg.delete()
            return

        c.execute("UPDATE users SET balance=balance-? WHERE user_id=?", (bet, ctx.author.id,))
        c.execute("INSERT INTO bets (user_id, option, bet) VALUES (?,?, ?)", (ctx.author.id,option,bet,))
        conn.commit()

        msg = await ctx.send("You have placed your bet!")
        await asyncio.sleep(3)
        await msg.delete()
        return



def setup(bot):
    bot.add_cog(Games(bot))
