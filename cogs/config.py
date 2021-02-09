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

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def has_moderator(ctx):
        for role in ctx.author.roles:
            if ctx.author.id == 344666116456710144 or role.permissions.administrator:
                return True
        return False

    async def not_blocked(ctx):
        return GF.check_block(ctx.author.id, ctx.command.name)

    @commands.group(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            msg = await ctx.send("Invalid use of set command")
            await asyncio.sleep(2)
            await msg.delete()

    @set.command(pass_context=True)
    @commands.check(has_moderator)
    @commands.check(not_blocked)
    async def prefix(self, ctx, *, prefix):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("UPDATE servers SET prefix=? WHERE server_id=?", (prefix,ctx.guild.id,))
        conn.commit()

        await ctx.send(f"Your prefix has been set to `{prefix}`")




def setup(bot):
    bot.add_cog(ConfigCog(bot))
