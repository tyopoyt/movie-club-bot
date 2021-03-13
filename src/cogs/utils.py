import discord
import sys
import json
import pprint
from datetime import timedelta
from datetime import datetime
from discord.ext import commands
from utils.color_util import magenta, red, green

def setup(movie_bot):
    movie_bot.add_cog(Utilities(movie_bot))

class Utilities(commands.Cog):
    movie_bot = None
    pp = None

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot
        self.pp = pprint.PrettyPrinter(depth=6)

    @commands.command(hidden=True)
    async def members(self, context):
        self.pp.pprint(context.message.guild.members)

    @commands.command(aliases=['dms'])
    async def dm(self, context):
        user = context.message.author.id
        await context.message.delete()

        dm_file = open('savedata\\dms.json','r')
        dms_dict = json.loads(dm_file.read())
        dm_file.close()

        if user not in dms_dict['dms']:
            dms_dict['dms'].append(user)
            dm_file = open('savedata\\dms.json','w')
            dm_file.write(json.dumps(dms_dict))
            dm_file.close()
            await context.message.author.send("I'll send you dms when a new poll is created.")
        else:
            await context.message.author.send("You're already receiving dms when new polls are created.")

    @commands.command(aliases=['nodms'])
    async def nodm(self, context):
        user = context.message.author.id
        await context.message.delete()

        dm_file = open('savedata\\dms.json','r')
        dms_dict = json.loads(dm_file.read())
        dm_file.close()

        user = context.message.author.id
        if user not in dms_dict['dms']:
            await context.message.author.send("You weren't opted in to receive dms.")
        else:
            dms_dict['dms'].remove(user)
            dm_file = open('savedata\\dms.json','w')
            dm_file.write(json.dumps(dms_dict))
            dm_file.close()
            await context.message.author.send("You'll no longer receive dms when new polls are created.")         

    @commands.command()
    async def ping(self, context):
        await context.channel.send('Pong!')

    @commands.command()
    @commands.guild_only()
    async def prefix(self, context, arg):
        self.movie_bot.command_prefix = arg
        await context.channel.send(f'The prefix is now {self.movie_bot.command_prefix}')

    @commands.command()
    async def time(self, context):
        await context.channel.send(f"Bot's local time is: {datetime.now().strftime('%a, %d %b %H:%M:%S')}")

    @commands.command(hidden= True, aliases=['purge', 'remove'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, context, amount='5'):
        try:
            amt = int(amount)
            await context.channel.purge(limit=amt + 1)
        except:
            await context.channel.send(f'\"{amount}\" is not a number')

    @commands.command(hidden=True, aliases=['samoht'])
    async def thomas(self, context):
        await context.channel.send("**Quoth White Thomas,** \"*I guess you forgot about the time you and Bravo company left my white ass for dead, huh? But I remember. I remember everything. I remember Vietnam like it was yesterday. I remember that village in Tainan that we cut down. It was a massacre. All the dead Chinamen we left in our tracks. I remember the faces, the children. This one child I'll never forget. Poor little bastard was still alive. His little Chinese legs were blown clean off! Still see his little shins & feet hanging from the ceiling fan across the hut. He was charred from his head down to his little Chinese knees. He tried to get up, but he fell over when what was left of his right leg broke off. As he laid there, flat on his face, he looked up at me. His little Chinese eyes burned right into my stomach, deep into my soul. He said something to me in Chinese like, 'Boo coo sow!', sounded like some cartoon shit. But I understood it to be a question that he was asking me. And I don't have to know how to speak Chinese to know what that question was. 'Why, White Thomas? Why?'* \"")
