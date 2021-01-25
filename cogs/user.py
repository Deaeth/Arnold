import discord
import asyncio
import time
import random
import sqlite3
import os.path
import wikipediaapi
import json
from .GlobalFunctions import GlobalFunctions as GF
from discord.utils import get

from discord.ext import commands

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def checkUser(self, c, userId):
        c.execute("SELECT * FROM team WHERE user_id=?", (userId,))
        row = c.fetchone()

        if row:
            return False
        return True

    async def not_blocked(ctx):
        return GF.check_block(ctx.author.id, ctx.command.name)


    @commands.command(name="ob")
    @commands.check(not_blocked)
    async def ob(self, ctx, *, names):
        obServer = self.bot.get_guild(737104128777650217)
        names = names.split()
        #I think i have to do this i had problems with the str idk
        response = ""
        for name in names:
            for emoji in obServer.emojis:
                emojiName = emoji.name.replace("OB_", "")
                if emojiName.lower() == name.lower():
                    response = response + " " + str(emoji)
        await ctx.send(response)
        await ctx.message.delete()

    @commands.command(name="pomodoro")
    @commands.check(not_blocked)
    async def pomodoro(self, ctx, cycles: int):
        user = UserAccount(ctx.author.id)
        for x in range(cycles):
            breakTime = 0
            pomRole = get(ctx.guild.roles, name="Pomodoro 🍅")
            adminRoles = []

            user.add_pomodoro(1)
            await ctx.send("Starting cycle {} 25 minutes".format(str(x+1)))

            await ctx.author.add_roles(pomRole, reason="Pomodoro", atomic=True)

            for role in ctx.author.roles:
                if role.permissions.administrator:
                    try:
                        await ctx.author.remove_roles(role, reason="Pomodoro Block")
                        adminRoles.append(role)
                    except:
                        continue

            await asyncio.sleep(10)

            await ctx.author.remove_roles(pomRole, reason="Pomodoro", atomic=True)

            for role in adminRoles:
                await ctx.author.add_roles(role, reason="Pomodoro Unblock", atomic=True)

            if x % 4 == 0:
                breakTime = 60 * 25
                await ctx.send("Starting break {} (25 minutes)".format(str(x+1)))

            breakTime = 60 * 5
            await ctx.send("Starting break {} (5 minutes)".format(str(x+1)))
            await asyncio.sleep(breakTime)

    @commands.command(name="wiki")
    @commands.check(not_blocked)
    async def wiki(self, ctx, *, search):

        loopCount = 0
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(search)

        if not page.exists():
            await ctx.send("Page doesn't exist")
            return

        if len(page.sections) > 1:
            embed = discord.Embed(name='Sections', description="Pick one of these sections", colour=0xc7e6a7)
            for s in page.sections:
                if loopCount > 8: break;
                embed.add_field(name=str(loopCount), value=s.title, inline=False)
                loopCount+=1
            await ctx.send(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            except asyncio.TimeoutError:
                return
            else:
                try:
                    section = page.sections[int(msg.content)]
                    embed = discord.Embed(name=section.title, colour=0xc7e6a7)
                    embed.add_field(name="Results: ", value=section.text[0:400] + "...")
                    await ctx.send(embed=embed)
                except Exception as e:
                    print("ERR: ", e)
                    await ctx.send("Your answer was invalid ")
        else:

            embed = discord.Embed(title=search.capitalize(), colour=0xc7e6a7)
            embed.add_field(name="Results:", value=page.summary[0:400] + "...")

            await ctx.send(embed=embed)


    @commands.command(name="roulette")
    @commands.check(not_blocked)
    async def roulette(self, ctx):
        roll = random.randint(1, 6)
        if roll == 3:
            await ctx.send("{} has been shot!".format(ctx.author.mention))
            await ctx.author.ban(delete_message_days=0)

        else:
            await ctx.send("You're safe!")
            #conn = sqlite3.connect(db_path)
            #c = conn.cursor()
            #print(ctx.author.id)
            #c.execute("UPDATE users SET balance=balance + ? WHERE user_id=?", (1000, ctx.author.id,))
            #conn.commit()

    @commands.group(pass_context=True)
    @commands.check(not_blocked)
    async def money(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use of money command")

    @commands.command(name="leaderboard")
    @commands.check(not_blocked)
    async def leaderboard(self, ctx, type):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        try:
            c.execute("SELECT user_id, {} FROM users ORDER BY {} DESC LIMIT 5".format(type, type))
            top = c.fetchall()

            embed = discord.Embed(title="Leaderboard for {}".format(type))
            for user in top:
                embed.add_field(name=self.bot.get_user(user[0]).name, value="Amount: {}".format(user[1]), inline=False)
            await ctx.send(embed=embed)
        except sqlite3.OperationalError:
            await ctx.send("There is no leaderboard for that type")

    @money.command(pass_context=True)
    @commands.check(not_blocked)
    async def balance(self, ctx):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=?", (ctx.author.id,))
        row = c.fetchall()

        await ctx.send("You have {} coins".format(row[0][2]))

    @commands.group(pass_context=True)
    @commands.check(not_blocked)
    async def tourney(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid use of tourney command")

    @tourney.command(pass_context=True)
    @commands.check(not_blocked)
    async def show(self, ctx, name, round):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM tournaments WHERE name=?", (name,))
        tournament = c.fetchone()
        tournamentId = tournament[0]

        c.execute("SELECT * FROM matches WHERE tourney_id=? AND round=?", (tournamentId, int(round),))
        matches = c.fetchall()


        embed = discord.Embed(title=("Tournament: {}".format(tournament[1])), colour=0xc7e6a7)
        for match in matches:
            embed.add_field(name="Team 1", value="<@{}>".format(str(match[2])), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="Team 2", value="<@{}>".format(str(match[3])), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=False)
        await ctx.send(embed=embed)


    @tourney.command(pass_context=True)
    @commands.check(not_blocked)
    async def create(self, ctx, name, users: int):


        if not (users & (users-1) == 0) or users < 4:
            await ctx.send("User count must be at least 4 and a power of 2")
            return


        tourney = []
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT 1 FROM tournaments WHERE host_id=?", (ctx.author.id,))
        row = c.fetchone()

        if row != None:
            await ctx.send("You're already hosting a tourney!")
            return

        if await self.checkUser(c, ctx.author.id): c.execute("INSERT INTO team (name, user_id, wins) VALUES (?, ?, 0)", (ctx.author.name, ctx.author.id,))
        c.execute("INSERT INTO tournaments (name, host_id, rounds) VALUES (?, ?, ?)", (name, ctx.author.id, users))
        c.execute("SELECT 1 FROM tournaments WHERE host_id=?", (ctx.author.id,))
        row = c.fetchone()
        tourneyId = row[0]




        matchCount = users / 2
        roundCount = 1
        while matchCount >= 1:
            for x in range (int(matchCount)):
                print(x)
                c.execute("INSERT INTO matches (tourney_id, round) VALUES (?, ?)", (tourneyId,roundCount,))
            matchCount = matchCount / 2
            roundCount += 1

                #matches["match_" + str(x)] = {"player_one": "null", "player_two": "null"}

            #tourney[x] = matches


        conn.commit()
        await ctx.send("Tournament {} has been created, make sure to get {} to join".format(name, str(users)))


    @tourney.command(pass_context=True)
    @commands.check(not_blocked)
    async def join(self, ctx, tourneyName):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if await self.checkUser(c, ctx.author.id): c.execute("INSERT INTO team (name, user_id, wins) VALUES (?, ?, 0)", (ctx.author.name, ctx.author.id,))
        c.execute("SELECT 1 FROM tournaments WHERE name=?", (tourneyName,))
        row = c.fetchone()

        if not row:
            await ctx.send("That tournament doesn't exist!")
            return

        tourneyId = row[0]

        c.execute("SELECT 1 FROM matches WHERE tourney_id=? AND team_1=? OR team_2=?", (tourneyId,ctx.author.id, ctx.author.id,))
        row = c.fetchone()

        if row:
            await ctx.send("You're already in it!")
            return


        sql = """
            UPDATE
                matches
            SET team_{}= ?
            WHERE id = (
                SELECT MIN(id)
                FROM matches
                WHERE (team_{} IS NULL)
            )
            AND
            tourney_id=?
        """
        c.execute(sql.format("1", "1"), (ctx.author.id,tourneyId,))

        if c.rowcount < 1:

            c.execute(sql.format("2", "2"), (ctx.author.id,tourneyId,))
            if c.rowcount < 1:
                await ctx.send("Tourney is full!")
                return

        conn.commit()
        await ctx.send("You have joined the tourney {}".format(tourneyName))
        return


    @commands.command(name="suggest")
    @commands.check(not_blocked)
    async def suggestion(self, ctx, *, suggestion):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO suggestions (user_id, suggestion, status) VALUES (?, ?, ?)", (ctx.author.id, suggestion, "incomplete"))
        conn.commit()
        await ctx.send("Your suggestion has been dumped in the trash!")

    @commands.command(name="fortune")
    @commands.check(not_blocked)
    async def fortune(self, ctx):
        with open("imports.json", 'r') as f:
            json_data = json.load(f)
            fortunes = json_data["fortunes"]
            await ctx.send(random.choice(fortunes))

def setup(bot):
    bot.add_cog(UserCog(bot))
