import discord
import os
import json
from utils.color_util import *
from discord.ext import commands

movie_bot = commands.Bot(command_prefix='!')

@movie_bot.event
async def on_ready():
    print('Logged on as ' + blue(str(movie_bot.user)))

@movie_bot.command(hidden=True, aliases=['relaod'])
async def reload(context):
    if str(context.message.author) in admins:
        await context.message.delete()
        reload_cogs()
    else:
        await context.message.delete()
        await context.channel.send(context.message.author.mention + ' you do not have access to this command.')

def load_cogs():
    for filename in os.listdir('src\\cogs'):
        if filename.endswith('.py'):
            print('Loading ' + yellow(filename[:-3]) + ' cog')
            movie_bot.load_extension(f'cogs.{filename[:-3]}')

def reload_cogs():
    for filename in os.listdir('src\\cogs'):
        if filename.endswith('.py'):
            print('Reloading ' + yellow(filename[:-3]) + Fore.WHITE + ' cog')
            movie_bot.reload_extension(f'cogs.{filename[:-3]}')

# setup and login
print('Initializing', dark_blue('M') + blue('o') + dark_cyan('v') + cyan('i') + dark_green('e'), green('C') + dark_yellow('l') + yellow('u') + red('b'), dark_red('B') + magenta('o') + pink('t') + charcoal('...'))
config_file = open('src\\config.json','r')
config = json.loads(config_file.read())
auth = config['auth']
admins = config['admins']
config_file.close()

load_cogs()
movie_bot.run(auth['discord'])
