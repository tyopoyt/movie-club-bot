import discord
import os
import json
from colorama import Fore
from discord.ext import commands

movie_bot = commands.Bot(command_prefix='!')

@movie_bot.event
async def on_ready():
    print('Logged on as ' + Fore.BLUE + str(movie_bot.user) + Fore.WHITE)

@movie_bot.command(hidden=True, aliases=['relaod'])
async def reload(context):
    if str(context.message.author) in admins:
        await context.channel.purge(limit=1)
        reload_cogs()
    else:
        await context.channel.purge(limit=1)
        await context.channel.send(context.message.author.mention + ' you do not have access to this command.')

def load_cogs():
    for filename in os.listdir('src\\cogs'):
        if filename.endswith('.py'):
            print('Loading ' + Fore.YELLOW + filename[:-3] + Fore.WHITE + ' cog')
            movie_bot.load_extension(f'cogs.{filename[:-3]}')

def reload_cogs():
    for filename in os.listdir('src\\cogs'):
        if filename.endswith('.py'):
            print('Reloading ' + Fore.YELLOW + filename[:-3] + Fore.WHITE + ' cog')
            movie_bot.reload_extension(f'cogs.{filename[:-3]}')

# setup and login
config_file = open('src\\config.json','r')
config = json.loads(config_file.read())
auth = config['auth']
admins = config['admins']
config_file.close()

load_cogs()
movie_bot.run(auth['discord'])
