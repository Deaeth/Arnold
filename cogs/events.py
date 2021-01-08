from discord.ext import commands
import discord
import datetime

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Wenis is gay, and cringe. Gluce was here.

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

    async def is_server(ctx):
        return ctx.guild.id == 774751718754877480

    @commands.Cog.listener()
    async def on_message(self, message):

        copypasta = """I'd just like to interject for a moment. What you're referring to as Linux, is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital system components comprising a full OS as defined by POSIX.

Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn of events, the version of GNU which is widely used today is often called "Linux", and many of its users are not aware that it is basically the GNU system, developed by the GNU Project.

There really is a Linux, and these people are using it, but it is just a part of the system they use. Linux is the kernel: the program in the system that allocates the machine's resources to the other programs that you run. The kernel is an essential part of an operating system, but useless by itself; it can only function in the context of a complete operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically GNU with Linux added, or GNU/Linux. All the so-called "Linux" distributions are really distributions of GNU/Linux."""

        if message.content.strip() ==  copypasta:
            await message.channel.send("SHUT THE FUCK UP ABOUT LINUX")
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
