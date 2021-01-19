import discord
import os
from colorama import Fore
from discord.ext import commands

movie_bot = commands.Bot(command_prefix='!')

@movie_bot.event
async def on_ready():
    print('Logged on as ' + Fore.BLUE + str(movie_bot.user) + Fore.WHITE)

@movie_bot.command()
async def ping(context):
    await context.channel.send('Pong!')

@movie_bot.command()
async def prefix(context, arg):
    movie_bot.command_prefix = arg
    await context.channel.send(f'The prefix is now {movie_bot.command_prefix}')

@movie_bot.command()
async def time(context):
    import time
    await context.channel.send(f"Bot's local time is: {time.time()}")

@movie_bot.command()
async def clear(context, amount='5'):
    try:
        amt = int(amount)
        await context.channel.purge(limit=amt + 1)
    except:
        await context.channel.send(f'\"{amount}\" is not a number')

# setup and login
authfile = open('src\\auth.txt','r')
auth = authfile.read()
authfile.close()

for filename in os.listdir('src\\cogs'):
    if filename.endswith('.py'):
        print('Loading ' + Fore.YELLOW + filename[:-3] + Fore.WHITE + ' cog')
        movie_bot.load_extension(f'cogs.{filename[:-3]}')

movie_bot.run(auth)