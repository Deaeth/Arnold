from discord.ext import commands
import discord
import datetime
import sqlite3
import os
import asyncio
import requests
from discord.utils import get
from .classes.UserAccount import UserAccount

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

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)
        print()

        game = discord.Game("with the ban command!")
        await self.bot.change_presence(status=discord.Status.idle, activity=game)

        news_channel = self.bot.get_channel(803014275445948436)

        url = "https://newscatcher.p.rapidapi.com/v1/latest_headlines"

        querystring = {"lang":"en","media":"True"}

        headers = {
            'x-rapidapi-key': "96a071e9fdmsh57907bfaf371ddap156ac1jsn94803889484b",
            'x-rapidapi-host': "newscatcher.p.rapidapi.com"
            }
        print("requesting")

        while True:
            try:
                articles = []
                response = requests.request("GET", url, headers=headers, params=querystring)
                articles = response.json()["articles"]
                for article in articles:
                    embed = discord.Embed(title=article["title"], colour=0xc7e6a7, timestamp=datetime.datetime.strptime(article["published_date"], "%Y-%m-%d %H:%M:%S"))
                    embed.add_field(name="Summary", value=article["summary"][0:250] + "...", inline=False)
                    embed.add_field(name="Link", value="[Source]({})".format(article["link"]))

                    if article["media_content"] != None:
                        embed.set_thumbnail(url=article["media_content"])

                    await news_channel.send(embed=embed)
                    await asyncio.sleep(60*5)
            except Exception as e:
                print(e)
                pass

            await asyncio.sleep(60*5)


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = await ctx.send("You're on cooldown")
            await asyncio.sleep(2)
            await msg.delete()
            return
        print(error)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if member.id ==344666116456710144 and after.channel == None:
                voiceClient = get(self.bot.voice_clients, guild=before.channel.guild)
                await voiceClient.disconnect()
                return
            if member.id ==344666116456710144:
                channel = after.channel
                voiceClient = get(self.bot.voice_clients, guild=channel.guild)
                if voiceClient and voiceClient.is_connected():
                    await voiceClient.move_to(channel)
                else:
                    vc = await channel.connect()
        except:
            return
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            user = UserAccount(message.author.id)
            user.add_points(len(message.content.split()))
        return


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



def setup(bot):
    bot.add_cog(Events(bot))
