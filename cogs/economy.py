from discord.ext import commands
import discord
import datetime
import sqlite3
import os
from .GlobalFunctions import GlobalFunctions as GF
from .classes.UserAccount import UserAccount

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def not_blocked(ctx):
        return GF.check_block(ctx.author.id, ctx.command.name)

    @commands.command(name="work")
    @commands.check(not_blocked)
    @commands.cooldown(1, (60*60), commands.BucketType.user)
    async def work(self, ctx):
        user = UserAccount(ctx.author.id)
        user.change_money(100, "add")

        await ctx.send("You just worked for 100 coins, nice")
        return

    @commands.command(name="give")
    @commands.cooldown(1, (10), commands.BucketType.user)
    async def give(self, ctx, user: discord.Member, amount: int):
        sender = UserAccount(ctx.author.id)
        reciever = UserAccount(user.id)
        if (sender.get_balance()) >= amount:
            sender.change_money(amount, "subtract")
            reciever.change_money(amount, "add")
            await ctx.send("Your transaction was successful")
        else:
            await ctx.send("You don't have {}".format(amount))



def setup(bot):
    bot.add_cog(Economy(bot))
