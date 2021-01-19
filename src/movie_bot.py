import discord
import os
from colorama import Fore
from discord.ext import commands

movie_bot = commands.Bot(command_prefix='!')

@movie_bot.event
async def on_ready():
    print('Logged on as ' + Fore.BLUE + str(movie_bot.user) + Fore.WHITE)

# setup and login
authfile = open('src\\auth.txt','r')
auth = authfile.read()
authfile.close()

for filename in os.listdir('src\\cogs'):
    if filename.endswith('.py'):
        print('Loading ' + Fore.YELLOW + filename[:-3] + Fore.WHITE + ' cog')
        movie_bot.load_extension(f'cogs.{filename[:-3]}')

movie_bot.run(auth)