from discord.ext import commands
import discord
import asyncio
import os
from discord.utils import get
from discord.ext import commands
from discord.utils import get

class CogControl(commands.Cog):

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



def setup(bot):
    bot.add_cog(CogControl(bot))
