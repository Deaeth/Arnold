import discord
from discord.ext import commands

intents = discord.Intents().all()

bot = commands.Bot(command_prefix='$', intents=intents);

initial_extensions = ["cogs.owner", "cogs.moderation", "cogs.user", "cogs.events"]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

#@bot.check
#async def blockDms(ctx):
#    return ctx.guild is not None;

#0xc7e6a7 is the standard hex for embed

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    game = discord.Game("with the ban command!")
    await bot.change_presence(status=discord.Status.idle, activity=game)

    print(f'Successfully logged in and booted...!')

bot.run("NjEyMDQyNzI1OTAyMTIzMDIw.XVcnNQ.YW7-myX1tWXNRZLdbTv9cKYWLD0",bot=True, reconnect=True)
