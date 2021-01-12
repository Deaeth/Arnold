from discord.ext import commands
import discord
import asyncio
import sqlite3
import os
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

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def _cog_load(self, ctx, *, cog: str):
        #loads a cog
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def _cog_unload(self, ctx, *, cog: str):
        #unloads a cog
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _cog_reload(self, ctx, *, cog: str):
        #reloads a cog
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

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

        async def check(m):
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





    @commands.command(name='showsuggestions', hidden=True)
    @commands.is_owner()
    async def showsuggestions(self, ctx, status):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM suggestions WHERE status=?", (status,))
        suggestions = c.fetchall()

        if suggestions:
            embed = discord.Embed(title="Suggestions", colour=0xc7e6a7, description=status)
            for suggestion in suggestions:
                embed.add_field(name="\u200b", value="<@{}>\n{}".format(str(suggestion[1]), suggestion[2]))
            await ctx.send(embed=embed)
        else:
            await ctx.send("No suggestions found")


def setup(bot):
    bot.add_cog(OwnerCog(bot))
