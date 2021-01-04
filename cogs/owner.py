from discord.ext import commands
import discord
import asyncio
import sqlite3
import os
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
