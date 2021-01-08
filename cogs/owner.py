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

    @commands.command(name="database")
    @commands.is_owner()
    async def database(self, ctx):
        guild = ctx.guild
        for member in guild.members:
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


    @commands.command(name="createcasino")
    @commands.is_owner()
    async def createcasino(self, ctx, question, option_one, option_two, timeLimit):
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

    @commands.command(name="payout")
    @commands.is_owner()
    async def payout(self, ctx, option, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        multiplier = 0
        id = int(id)
        option = int(option)

        c.execute("SELECT * FROM bets WHERE casino_id=? AND option=1", (id,))
        option_one = c.fetchall()
        print(option_one)

        c.execute("SELECT * FROM bets WHERE casino_id=? AND option=2", (id,))
        option_two = c.fetchall()

        if option == 1:
            multiplier = (100 - ((len(option_one) / (len(option_one) + len(option_two))) * 100)) + 1
            for row in option_one:
                print(user_id)
                user_id = row[1]
                bet = row[3]
                c.execute("UPDATE users SET balance = ? + ? * ? WHERE user_id=?", (bet,bet,multiplier,user_id,))
                conn.commit()
        else:

            multiplier = (100 - ((len(option_one) / (len(option_one) + len(option_two))) * 100)) + 1
            for row in option_one:
                user_id = row[1]
                bet = row[3]
                c.execute("UPDATE users SET balance = ? + ? * ? WHERE user_id=?", (bet,bet,multiplier,user_id,))
                conn.commit()

        c.execute("DELETE FROM casino WHERE casino_id=?", (id,))
        c.execute("DELETE FROM bets WHERE casino_id=?", (id,))
        conn.commit()

        await ctx.send("OPTION {} HAS WON WITH A MULTIPLIER OF {}".format(option, multipler))
        return




def setup(bot):
    bot.add_cog(OwnerCog(bot))
