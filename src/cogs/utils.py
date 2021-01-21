import discord
from datetime import datetime
from discord.ext import commands

class Utilities(commands.Cog):
    movie_bot = None

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

    @commands.command()
    async def ping(self, context):
        await context.channel.send('Pong!')

    @commands.command()
    async def prefix(self, context, arg):
        self.movie_bot.command_prefix = arg
        await context.channel.send(f'The prefix is now {self.movie_bot.command_prefix}')

    @commands.command()
    async def time(self, context):
        await context.channel.send(f"Bot's local time is: {datetime.now().strftime('%a, %d %b %H:%M:%S')}")

    @commands.command(aliases=['purge', 'remove'])
    async def clear(self, context, amount='5'):
        try:
            amt = int(amount)
            await context.channel.purge(limit=amt + 1)
        except:
            await context.channel.send(f'\"{amount}\" is not a number')

def setup(movie_bot):
    movie_bot.add_cog(Utilities(movie_bot))
