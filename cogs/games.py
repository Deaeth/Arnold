from discord.ext import commands
import discord
import os
import sqlite3
import asyncio
import time
import random
from .GlobalFunctions import GlobalFunctions as GF

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

    async def has_moderator(ctx):
        for role in ctx.author.roles:
            if role.id == 779430696510160936  or ctx.author.id == 344666116456710144:
                return True
        return False

    async def not_blocked(ctx):
        return GF.check_block(self, ctx.author.id, ctx.command.name)


    @commands.command(name="coinflip")
    @commands.check(not_blocked)
    async def coinflip(self, ctx):
        winner = random.randint(0, 1)
        if (winner == 0):
            await ctx.send("It's Heads!")
        else:
            await ctx.send("It's Tails!")
        return

    @casino.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def create(self, ctx, question, option_one, option_two, timeLimit):
        origMsg = await ctx.send("**NEW CASINO BET**\n*Open for {} seconds*\n\n**QUESTION**: {}\nOption One: {}\nOption Two: {}".format(timeLimit, question, option_one, option_two))

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO casino (casino_id, status) VALUES (?,?)", (ctx.author.id,"active",))
        conn.commit()

        await asyncio.sleep(int(timeLimit))
        await origMsg.edit(content="**NEW CASINO BET**\n*Casino is closed*\n\n**QUESTION**: {}\nOption One: {}\nOption Two: {}".format(question, option_one, option_two))
        c.execute("UPDATE casino SET status=? WHERE casino_id=?", ("inactive",ctx.author.id))
        conn.commit()
        return

    @casino.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def payout(self, ctx, option, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        multiplier = 0
        id = int(id)
        option = int(option)

        await ctx.delete()

        c.execute("SELECT * FROM bets WHERE option=1")
        option_one = c.fetchall()
        print(option_one)

        c.execute("SELECT * FROM bets WHERE option=2")
        option_two = c.fetchall()

        if option == 1:
            if len(option_one) == 0:
                await ctx.send("No one voted for this one!")
                return
            else:
                multiplier = (100 - ((len(option_one) / (len(option_one) + len(option_two))) * 100)) / 100 + 1
                for row in option_one:
                    print(row, row[2], row[4])
                    user_id = row[2]
                    bet = row[4]
                    c.execute("UPDATE users SET balance = balance + (? * ?) WHERE user_id=?", (bet,multiplier,user_id,))
                    conn.commit()
        else:
            if len(option_two) == 0:
                await ctx.send("No one voted for this one!")
                return
            else:
                multiplier = (100 - ((len(option_two) / (len(option_one) + len(option_two))) * 100)) / 100 + 1
                for row in option_two:
                    user_id = row[2]
                    bet = row[4]
                    c.execute("UPDATE users SET balance = balance + (? * ?) WHERE user_id=?", (bet,multiplier,user_id,))
                    conn.commit()

        c.execute("DELETE FROM casino WHERE casino_id=?", (id,))
        c.execute("DELETE FROM bets")
        conn.commit()

        await ctx.send("OPTION {} HAS WON WITH A MULTIPLIER OF {}".format(option, multiplier))
        return

    @casino.command(pass_context=True)
    @commands.check(not_blocked)
    async def join(self, ctx, option, bet):
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


    @commands.command(name = "slotmachine")
    @commands.check(not_blocked)
    async def slotmachine(self,ctx):
        outcomes = ["<:OB_ratdog:737111061722955807>","<:OB_mike:737105902720647258>","<:OB_monkastare:755857538632777899>"]
        randomOutcomes = random.choices(outcomes, weights=(62, 48,84), k=3)
        msg = ""
        if randomOutcomes[0] == randomOutcomes[1] == randomOutcomes[2]:
            msg = "**YOU WIN!**" + " " + "<:OB_hasCapital:790800758207021126> <a:OB_winetime:796556837981257778>"
        else:
            msg = "**LOSER!**" + " " + "<:OB_bebela:737110263836311733> <a:OB_teatime:737109485302055003>"
        message = await ctx.send("❎❎❎")
        await asyncio.sleep(1)
        await message.edit(content=randomOutcomes[0] + randomOutcomes[1] + randomOutcomes[2])
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Games(bot))
