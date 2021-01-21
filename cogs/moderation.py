import discord
import asyncio
import datetime
import sqlite3
import os
from discord.ext import commands
from discord.utils import get
from .GlobalFunctions import GlobalFunctions as GF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_log(self, moderator: discord.Member, user: discord.Member, command, reason):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        date = datetime.datetime.now()

        c.execute("INSERT INTO logs (user_id, moderator_id, action, reason, date) VALUES (?,?,?,?, ?)", (user.id, moderator.id, command, reason, date,))
        conn.commit()

        image = user.avatar_url
        embed = discord.Embed(title=command, timestamp=date, color=0x2403fc)
        embed.set_thumbnail(url=image)
        embed.add_field(name="Moderator", value=moderator, inline=True)
        embed.add_field(name="User", value=user, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)


        channel = self.bot.get_channel(789724879809019904)
        await channel.send(embed=embed)



    def get_length(self, textTime):
        textTime = textTime.lower()
        milliseconds = 0

        if textTime.find("d") != -1:
            intTime = textTime.replace("d","")
            intTime = int(intTime)
            milliseconds = 86400 * (int(intTime))

        elif textTime.find("h") != -1:
            intTime = textTime.replace("h","")
            intTime = int(intTime)
            milliseconds = milliseconds + 3600 * (int(intTime))

        elif textTime.find("m") != -1:
            intTime = textTime.replace("m","")
            intTime = int(intTime)
            milliseconds = 60  * (intTime)

        return milliseconds

    async def has_moderator(ctx):
        for role in ctx.author.roles:
            if role.id == 779430696510160936  or ctx.author.id == 344666116456710144 or role.id == 769842662580027452:
                return True
        return False

    async def not_blocked(ctx):
        return GF.check_block(ctx.author.id, ctx.command.name)


    @commands.command(name="rapsheet")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def rapsheet(self, ctx, user):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            user_id = int(user)

        except:
            try:
                user_id=ctx.message.mentions[0].id
            except:
                await ctx.send("You need to mention the user or type their id")
                return

        user = self.bot.get_user(user_id)
        image = user.avatar_url
        embed = discord.Embed(title="Rapsheet for {}".format(user.name), color=0x2403fc)

        embed.set_thumbnail(url=image)

        c.execute("SELECT * FROM logs WHERE user_id=?", (user_id,))
        rows = c.fetchall()

        if not rows:
            await ctx.send("That user has no infractions")
            return

        for x in range(5):
            row = rows[x]
            moderator = self.bot.get_user(row[2])
            action = row[3]
            date = row[4]
            reason = row[5]
            embed.add_field(name=row[3], value="Moderator: {}\nReason: {}\nDate: {}".format(moderator.name, reason, date), inline=False)
        embed.add_field(name="Account Created", value=user.created_at, inline=False)
        embed.set_footer(text="Total Infractions: {}".format(len(rows)))

        await ctx.send(embed=embed)

    @commands.command("poll")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def poll(self, ctx, question, timeLimit):
        yes_count = 0
        no_count = 0
        winner = ""

        await ctx.message.delete()
        origMsg = await ctx.send("**NEW Poll**\n*Open for {} seconds*\n\n**QUESTION**: {}".format(timeLimit, question))
        origMsg = discord.utils.get(self.bot.cached_messages, id=origMsg.id)

        await origMsg.add_reaction("✅")
        await origMsg.add_reaction("❌")

        await asyncio.sleep(int(timeLimit))

        for reaction in origMsg.reactions:
            if str(reaction.emoji) == "✅":
                yes_count = reaction.count
            elif str(reaction.emoji) == "❌":
                no_count = reaction.count

        if yes_count > no_count:
            winner = "Yes"
        elif no_count > yes_count:
            winner = "No"
        else:
            winner = "Tied"

        await origMsg.edit(content="**NEW Poll**\n*Closed*\n\n**QUESTION**: {}\n**WINNER**: {}".format(question, winner))
        return

    @commands.command(name="mute")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def mute(self, ctx, member: discord.Member, length, *, reason):
        print(member, length, reason)
        if member and length and reason:

            role = get(member.guild.roles, name="Muted 🔗")
            await member.add_roles(role, reason=reason, atomic=True)

            await ctx.message.delete()
            await ctx.send("{} has been muted for {}".format(member.mention, length))

            await asyncio.sleep(self.get_length(length))

            await member.remove_roles(role, reason = "time's up ")

        else:
            ctx.send("The command is `$mute *user* *length* *reason*`")


    @commands.command(name="unmute")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def unmute(self, ctx, member: discord.Member):

        if member:
            role = get(member.guild.roles, name="Muted 🔗")
            await member.remove_roles(role, reason = "time's up ")

            await ctx.send("<@{}> has been unmuted!".format(member.id))
        else:
            ctx.send("The command is `$mute *user* *length* *reason*`")

    @commands.command(name="ban")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def ban(self, ctx, member: discord.Member, *, reason):
        if member.id == 344666116456710144:
            await ctx.send("you cant ban my master <:OB_pogO:737105405976772680>")
            return
        await ctx.send("DRUMROLLLLL PLEASE.... <@{}> is being banned!".format(member.id))
        await ctx.send("Banning <@{}> in: ".format(member.id))
        for x in reversed(range(1, 6)):
            await asyncio.sleep(1)
            await ctx.send(str(x))
        await member.ban(reason=reason)
        await ctx.send("<a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> {} is banned! <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989> <a:CrabDance:776261171618643989>".format(member.name))

    @commands.command(name="dungeon")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def dungeon(self, ctx, member: discord.Member, *, reason):

        if member and reason:
            role = get(member.guild.roles, name="Dungeoned 🔗")
            await member.add_roles(role, reason=reason, atomic=True)

            await ctx.message.delete()
            await ctx.send("{} has been dungeoned".format(member.mention))

        else:
            ctx.send("The command is `$dungeon *user* *reason*`")

    @commands.command(name="release")
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def release(self, ctx, member: discord.Member):

        if member:
            role = get(member.guild.roles, name="Dungeoned 🔗")
            await member.remove_roles(role, reason = "released")

            await ctx.send("<@{}> has been released!".format(member.id))
        else:
            ctx.send("The command is `$release *user*`")

def setup(bot):
    bot.add_cog(ModerationCog(bot))
