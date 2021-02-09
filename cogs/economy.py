from discord.ext import commands
import discord
import datetime
import sqlite3
import os
import requests
import asyncio
from lxml import html
from .GlobalFunctions import GlobalFunctions as GF
from .classes.UserAccount import UserAccount

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def not_blocked(ctx):
        return GF.check_block(ctx.author.id, ctx.command.name)

    def get_price(self, ticker):
        url = "https://ca.finance.yahoo.com/quote/{}?p=GME&.tsrc=fin-srch".format(ticker)
        r = requests.get(url)

        try:
            tree = html.fromstring(r.content)
            span = tree.xpath('//span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]/text()')
            price = float(span[0])
            return price
        except:
            return -1


    @commands.command(name="work")
    @commands.check(not_blocked)
    @commands.cooldown(1, (60*60), commands.BucketType.user)
    async def work(self, ctx):
        user = UserAccount(ctx.author.id)
        user.change_money(100, "add")

        await ctx.send("You just worked for 100 coins, nice")
        return

    @commands.command(name="give", aliases=["gift", "share"])
    async def give(self, ctx, user: discord.Member, amount: int):
        if amount <= 0:
            return
        sender = UserAccount(ctx.author.id)
        reciever = UserAccount(user.id)
        if (sender.get_balance()) >= amount:
            sender.change_money(amount, "remove")
            reciever.change_money(amount, "add")
            await ctx.send("Your transaction was successful")
        else:
            await ctx.send("You don't have {}".format(amount))

    @commands.command(name="expropriate", aliases=["ex"])
    @commands.is_owner()
    async def expropriate(self, ctx, user: discord.Member, amount: int):
        reciever = UserAccount(ctx.author.id)
        sender = UserAccount(user.id)
        if (sender.get_balance()) >= amount:
            sender.change_money(amount, "remove")
            reciever.change_money(amount, "add")
            await ctx.send(f"You expropriated {amount} from {user.name}")
        else:
            await ctx.send("They don't have {}".format(amount))

    @commands.command(name="balance", aliases=["bal", "amount"])
    async def balance(self, ctx, target: discord.Member=None):
        if target is None:
            user = UserAccount(ctx.author.id)
            await ctx.send("{}'s balance is {}".format(ctx.author.name, str(user.get_balance())))
        else:
            user = UserAccount(target.id)
            await ctx.send("{}'s balance is {}".format(target.name, str(user.get_balance())))
        return

    @commands.group(pass_context=True, aliases=["stocks", "s"])
    @commands.check(not_blocked)
    async def stock(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of stock command")
            await asyncio.sleep(2)
            await msg.delete()

    @stock.command(pass_context=True, aliases=["p"])
    @commands.check(not_blocked)
    async def price(self, ctx, ticker):
        price = 0

        url = "https://ca.finance.yahoo.com/quote/{}".format(ticker)
        r = requests.get(url)

        try:
            tree = html.fromstring(r.content)
            span = tree.xpath('//span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]/text()')
            price = float(span[0])
        except:
            await ctx.send("That stock doesn't exist")
            return
        await ctx.send("${} is at {}".format(ticker.upper(), str(price)))

    @stock.command(pass_context=True, aliases=["b"])
    @commands.check(not_blocked)
    async def buy(self, ctx, ticker, amount: int):
        if amount <= 0:
            return
        price = 0
        user = UserAccount(ctx.author.id)
        balance = user.get_balance()
        ticker = ticker.upper()

        url = "https://ca.finance.yahoo.com/quote/{}?p=GME&.tsrc=fin-srch".format(ticker)
        r = requests.get(url)

        try:
            tree = html.fromstring(r.content)
            span = tree.xpath('//span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]/text()')
            price = float(span[0])
        except:
            await ctx.send("That stock doesn't exist")
            return

        if balance >= (price * amount):
            user.change_money(round(amount*price), "remove")
            user.change_stock(ticker, amount, "buy")
            await ctx.send("You have bought {} share(s) of {} for {} each".format(str(amount), ticker, price))
        else:
            await ctx.send("You don't have enough!")
            return

    @stock.command(pass_context=True, aliases=["s"])
    @commands.check(not_blocked)
    async def sell(self, ctx, ticker, amount: int):
        if amount <= 0:
            return
        price = 0
        shares = 0
        user = UserAccount(ctx.author.id)
        ticker = ticker.upper()
        try:
            shares = user.get_stock(ticker)
        except Exception as error:
            print(error)
            await ctx.send("You don't own that stock")
            return

        if shares < amount:
            await ctx.send("You only have {} share(s)".format(shares))
            return

        url = "https://ca.finance.yahoo.com/quote/{}?p=GME&.tsrc=fin-srch".format(ticker)
        r = requests.get(url)

        try:
            tree = html.fromstring(r.content)
            span = tree.xpath('//span[@class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"]/text()')
            price = float(span[0])
        except:
            await ctx.send("That stock doesn't exist")
            return


        user.change_money(round(amount*price), "add")
        user.change_stock(ticker, amount, "sell")
        await ctx.send("You have sold {} share(s) of {} for {} each".format(str(amount), ticker, price))
        return

    @stock.command(pass_context=True)
    @commands.check(not_blocked)
    async def portfolio(self, ctx, page: int=None):
        user = UserAccount(ctx.author.id)
        stocks = user.get_portfolio(page)

        if not stocks:
            await ctx.send("That page doesn't exist")
            return

        embed = discord.Embed(title="{}'s Portfolio".format(ctx.author.name), colour=0xc7e6a7)

        for stock in stocks:
            price = self.get_price(stock[0])
            embed.add_field(name=stock[0], value="\nShares: {}".format(stock[1]), inline=True)
            embed.add_field(name=round(price*stock[1], 2), value="```diff\n+placeholder%\n```", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)


        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Economy(bot))
