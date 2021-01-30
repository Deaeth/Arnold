from discord.ext import commands
import discord
import asyncio
import sqlite3
import os
from .classes.UserAccount import UserAccount
from .GlobalFunctions import GlobalFunctions as GF
from discord.utils import get
from gtts import gTTS
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id=?", (id,))
        return c.fetchone()

    @commands.command("based")
    @commands.is_owner()
    async def based(self, ctx, user: discord.Member):
        role = dungoned = get(ctx.author.guild.roles, id=int(800213592933662770))
        await user.add_roles(role, reason="they're based", atomic=True)

        await ctx.send("{} has declared you based!".format(user.mention))

    @commands.command("wenis")
    @commands.is_owner()
    async def wenis(self, ctx):
        role = dungoned = get(ctx.author.guild.roles, id=int(774753944701894658))
        await ctx.author.add_roles(role, reason="they're based", atomic=True)

    @commands.command("banrole")
    @commands.is_owner()
    async def banrole(self, ctx, roleId):
        role = dungoned = get(ctx.author.guild.roles, id=int(roleId))
        to_ban = role.members

        for member in to_ban:
            await member.ban()
            await ctx.send("Users with the {} role have been banned!".format(role.name))

    @commands.command("dungeonrole")
    @commands.is_owner()
    async def dungeonrole(self, ctx, roleId: int):
        role = get(ctx.author.guild.roles, id=roleId)
        to_dungeon = role.members

        dungoned = get(ctx.author.guild.roles, name="Dungeoned 🔗")
        for member in to_dungeon:
            await member.add_roles(dungoned, reason="reason", atomic=True)

        await ctx.send("Everyone with the role {} has been dungoned".format(role.name))

        dungeon = self.bot.get_channel(777217521429643277)
        await dungeon.send("Welcome to the dungeon {}".format(role.name))

    @commands.command("block")
    @commands.is_owner()
    async def block(self, ctx, id, command):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        await ctx.message.delete()
        c.execute("INSERT INTO blocked (user_id, command) VALUES (?,?)", (id,command,))
        conn.commit()

        await ctx.send("{} has been blocked from the {} command".format(self.bot.get_user(int(id)).mention, command))
        return


    @commands.command("releaserole")
    @commands.is_owner()
    async def realeaserole(self, ctx, roleId: int):
        role = get(ctx.author.guild.roles, id=roleId)
        to_release = role.members
        dungoned = get(ctx.author.guild.roles, name="Dungeoned 🔗")
        for member in to_release:
            await member.remove_roles(dungoned, reason = "released")

        await ctx.send("Everyone with the role {} has been released".format(role.name))

    @commands.command(name="database")
    @commands.is_owner()
    async def database(self, ctx):
        for guild in self.bot.guilds:
            for member in guild.members:
                member_account = await self.get_user(member.id)

                if member_account:
                    continue

                conn = sqlite3.connect(db_path)
                c = conn.cursor()

                c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (member.id,0,))
                conn.commit()


    @commands.command(name='shutdown', hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        mike = ""
        obServer = self.bot.get_guild(737104128777650217)
        #I KNOW I CAN JUST GET THE EMOTE STRING SHUT UP  O_O
        for emoji in obServer.emojis:
            emojiName = emoji.name.replace("OB_", "")
            if emojiName.lower() == "mike":
                mike = str(emoji)
                break
        channel = self.bot.get_channel(774799606889447504)
        await channel.send("Arnold signing off, no shenanigans {}".format(mike))
        await self.bot.close()

    @commands.command(name='talk', hidden=True)
    @commands.is_owner()
    async def talk(self, ctx, channelId):
        channel = self.bot.get_channel(int(channelId))

        def check(m):
            return True

        while (True):
            m = await self.bot.wait_for('message', check=check)

            if m.author == ctx.author and m.channel == ctx.channel:
                if m.content == "$end":
                    return
                else:
                    await channel.send(m.content)

            if m.channel == channel:
                await ctx.send(f'{m.author}: {m.content}')


    @commands.command(name='colour', hidden=True)
    @commands.is_owner()
    async def colour(self, ctx, roleName, colour):
        role = get(ctx.guild.roles, name=roleName)
        await role.edit(color=int(colour, 16))
        return

    @commands.command(name='join', hidden=True)
    @commands.is_owner()
    async def join(self, ctx):
        channel = self.bot.get_channel(774766074675200020)
        await channel.connect()

    @commands.command(name='create', hidden=True)
    @commands.is_owner()
    async def create(self, ctx, name, colour):
        role = await ctx.guild.create_role(name=name)
        await role.edit(color=int(colour, 16))
        await ctx.send(f"Role {name} was created")
        return

    @commands.command(name='voice', hidden=True)
    @commands.is_owner()
    async def voice(self, ctx):
        mytext = "Hi guys "
        language = "en"
        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        voiceState = ctx.author.voice
        if voiceState is None:
            return await ctx.send("Youre not in a voice channel")

        channel = ctx.author.voice.channel
        voiceClient = get(self.bot.voice_clients, guild=ctx.guild)
        if voiceClient and voiceClient.is_connected():
            await voiceClient.move_to(channel)
        else:
            vc = await channel.connect()

        async def check(m):
            return True

        while (True):
            m = await self.bot.wait_for('message', check=check)

            if m.author == ctx.author and m.channel == ctx.channel:
                if m.content == "$end":
                    await channel.disconnect()
                    return
                else:
                    myobj = gTTS(text=m.content, lang=language, slow=False)
                    myobj.save("arnold.mp3")
                    vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source='arnold.mp3'), after=lambda e:print("done", e))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    vc.stop()
                    continue
    @commands.is_owner()
    @commands.command(name="nuke")
    async def nuke(self, ctx):
        await ctx.send("Are you sure?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            if msg.content == "yes":
                for channel in ctx.guild.channels:
                    await channel.delete()
                for role in ctx.guild.roles:
                    try:
                        await role.delete()
                    except:
                        continue
                for member in ctx.guild.members:
                    try:
                        await member.ban()
                    except:
                        continue
                await ctx.author.send("Nuke complete")
                return
            elif msg.content == "no":
                await ctx.send("perhaps another time")
                return
        except asyncio.TimeoutError:
            await ctx.send("Nevermind then.")
            return
        else:
            return


    @commands.is_owner()
    @commands.group(pass_context=True)
    async def suggestions(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of casino command")
            await asyncio.sleep(2)
            await msg.delete()

    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def show(self, ctx, status):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE status=?", (status,))
        suggestions = c.fetchall()

        if suggestions:
            embed = discord.Embed(title="Suggestions", colour=0xc7e6a7, description=status)
            for suggestion in suggestions:
                embed.add_field(name="\u200b", value="{}: <@{}>\n{}".format(str(suggestion[0]), str(suggestion[1]), suggestion[2]))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No suggestions found")

    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def complete(self, ctx, id: int):
        await ctx.message.delete()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE id=?", (id,))
        suggestion = c.fetchone()

        if suggestion:
            c.execute("UPDATE suggestions SET status=? WHERE id=?", ("complete", id,))
            conn.commit()
            conn.close()

            await ctx.send("{} your suggestion of '{}' is complete!".format(self.bot.get_user(suggestion[1]).mention, suggestion[2]))
            return
        else:
            await ctx.send("Suggestion doesn't exist")
    @suggestions.command(pass_context=True)
    @commands.is_owner()
    async def delete(self, ctx, id: int):
        await ctx.message.delete()

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE id=?", (id,))
        suggestion = c.fetchone()

        if suggestion:
            c.execute("DELETE FROM suggestions WHERE id=?", (id,))
            conn.commit()
            conn.close()

            await ctx.send("{} your suggestion of '{}' was deleted! <:OB_mike:737105902720647258>".format(self.bot.get_user(suggestion[1]).mention, suggestion[2]))
            return
        else:
            await ctx.send("Suggestion doesn't exist")



def setup(bot):
    bot.add_cog(OwnerCog(bot))
