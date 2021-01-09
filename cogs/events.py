from discord.ext import commands
import discord
import datetime
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Wenis is gay, and cringe. Gluce was here.

    async def is_server(self, ctx):
        return ctx.guild.id == 774751718754877480

    async def get_user(self, id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id=?", (id,))
        return c.fetchone()


    async def create_log(self, title, name):

        embed = discord.Embed(title=title, timestamp=datetime.datetime.now(), color=0x2403fc)
        embed.add_field(name="Name", value=name)

        channel = self.bot.get_channel(789724879809019904)
        await channel.send(embed=embed)

    async def on_ready(self):
        print('Ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)
        print("Guilds: ", self.bot.guils)
        print()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 774751718754877480:
            channel = self.bot.get_channel(774799606889447504)
            await channel.send("{} has joined the server!".format(member.mention))

        member_account = await self.get_user(member.id)
        if member_account:
            return

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute("INSERT INTO users (user_id) VALUES (?)", (member.id,))
        conn.commit()

        return


    @commands.Cog.listener()
    @commands.check(is_server)
    async def on_guild_channel_delete(self, channel):

        await self.create_log("Deleted Channel", channel.name)

    @commands.Cog.listener()
    @commands.check(is_server)
    async def on_guild_channel_create(self, channel):

        await self.create_log("Created Channel", channel.name)

    @commands.Cog.listener()
    @commands.check(is_server)
    async def on_guild_role_create(self, role):

        await self.create_log("Created Role", role.name)

    @commands.Cog.listener()
    @commands.check(is_server)
    async def on_guild_role_delete(self, role):

        await self.create_log("Deleted Role", role.name)



def setup(bot):
    bot.add_cog(Events(bot))
