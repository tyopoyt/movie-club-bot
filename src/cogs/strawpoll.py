import discord
import asyncio
import requests
import json
from pprint import pprint
from utils.color_util import red, green, yellow, cyan
from datetime import datetime
from discord.ext import commands, tasks
from utils.discord_util import get_or_fetch_user
from utils.google_util import get_headers
# from cogs.google import get_headers

def setup(movie_bot):
    movie_bot.add_cog(Strawpoll(movie_bot))

class Strawpoll(commands.Cog):
    me_url = 'https://www.strawpoll.me/api/v2/polls'
    com_url = 'https://strawpoll.com/api/poll'
    com_delete_url = 'https://strawpoll.com/api/content/delete'
    headers = {}
    should_update = False
    ended = False
    timing_task = None
    movie_bot = None
    poll_message = None
    poll = None
    main_server = None
    dev_id = None

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot
        config_file = open('savedata\\config.json', 'r')
        configs = json.loads(config_file.read())
        self.headers['API-KEY'] = configs['auth']['com']
        self.main_server = configs['server_id']
        self.dev_id = configs['dev_id']
        config_file.close()

    # check the results of current poll and return a string that can be sent on discord
    def cur_results(self, prefix='', ended=False):
        if self.poll is None:
            poll_file = open('savedata\\poll.json','r')
            self.poll = json.loads(poll_file.read())
            poll_file.close()

        prefix = str(prefix).replace('[link]', self.poll['link'])

        message = prefix + f"\n```fix\nYou may have to refresh the page if the site says scripts are blocked.```\n**{'Final ' if ended else ''}Results:**\n```ini\n"
        highest = 0
        winners = []
        losers = []

        if self.poll['type'] == 'com':
            try:
                response = (requests.get(self.com_url + f"/{self.poll['data']['content_id']}").json())['content']
            except:
                print('Poll is ' + red('INVALID'))
                return 'Error: Current poll is invalid (Has it been ended?)'

            # check results of the poll
            #TODO: optimize this to show in order and use python's shit or maybe lodash
            for answer in response['poll']['poll_answers']:
                if answer['votes'] > highest:
                    highest = answer['votes']
                    losers.extend(winners)
                    winners = [{'answer': answer['answer'], 'votes': answer['votes']}]
                elif answer['votes'] == highest:
                    winners.append({'answer': answer['answer'], 'votes': answer['votes']})
                else:
                    losers.append({'answer': answer['answer'], 'votes': answer['votes']})
            
            # format results message
            for answer in winners:
                message += f"[ {answer['answer']}: {answer['votes']} votes ]\n"
            for answer in losers:
                message += f"; {answer['answer']}: {answer['votes']} votes\n"

            message += "```"

            if not ended:
                message += f"*(Updated {datetime.now().strftime('%a, %b %d  %H:%M:%S')} ET)*"
        else:
            try:                
                response = requests.get(self.me_url + f"/{self.poll['data']['id']}").json()
                # TODO: format results from .me
                message += '```'
            except:
                message = 'Error: Could not retrieve poll from strawpoll.me'

        return message

    @tasks.loop(minutes=1)
    async def result_updater(self):
        if not self.should_update:
            self.result_updater.stop()
            return
        try:
            await self.poll_message.edit(content=self.cur_results(self.poll_message.content[0:self.poll_message.content.find('\n```fix')]))
        except discord.errors.NotFound:
            print('Message ' + cyan('not found'))
            print('Loop ' + red('stopped'))
            self.should_update = False
        await asyncio.sleep(self.result_updater.seconds)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def makepoll(self, context, poll_type='com'): # , options=None): #TODO: in the future allow manual poll creation?
        usage = f'**Usage:** {self.movie_bot.command_prefix}makepoll [com/me] [title] > [poll options]'

        if not self.ended and self.poll is not None and self.poll['type'] == 'com':
            await self.end(context, True)

        def author_resp(message):
            return message.author == context.author and message.channel == context.channel

        await context.channel.send("What's the poll title?")
        title = (await self.movie_bot.wait_for('message', check=author_resp)).content
        # await context.channel.send("What are the options? (Comma separated)")
        # answers = (await self.movie_bot.wait_for('message', check=author_resp)).content.split(',')

        # answers = options.split(' ')
        
        answers = get_headers()
        self.ended = False
        self.poll = {}
        url = ''

        if poll_type == 'com':
            data = { 
                     "poll": { 
                         "title": title,
                         "answers": answers,
                         "ma": True
                         }
                    }
            response = requests.post(url=self.com_url, json=data, headers=self.headers)
            data = response.json()
            url = f'https://strawpoll.com/{data["content_id"]}/'

            self.poll['type'] = poll_type
            self.poll['link'] = url
            self.poll['data'] = data

            self.poll_message = await context.channel.send(self.cur_results(f'**{title}**: <{url}>'))

            if not self.should_update:
                self.should_update = True
                try:
                    self.result_updater.start()
                except:
                    self.result_updater.restart()

        elif poll_type == 'me':
            data = { 
                     "title": title,
                     "options": answers,
                     "multi": True,
                     "captcha": True
                   }
            response = requests.post(url=self.me_url, json=data)
            data = response.json()
            url = f'https://www.strawpoll.me/{data["id"]}/'

            self.poll['type'] = poll_type
            self.poll['link'] = url
            self.poll['data'] = data

            self.poll_message = await context.channel.send(f'**{title}:** {url}')

        else:
            await context.channel.send(f'Unrecongnized poll site.  Options: {self.movie_bot.command_prefix}makepoll com or {self.movie_bot.command_prefix}makepoll me\n(Default is me)')
            return

        poll_file = open('savedata\\poll.json','w')
        poll_file.write(json.dumps(self.poll))
        poll_file.close()        

        if context.guild.id == self.main_server:
            dms_file = open('savedata\\dms.json','r')
            dms = json.loads(dms_file.read())['dms']
            dms_file.close()

            for user_id in dms:
                user = await get_or_fetch_user(self, user_id)
                await user.send(f"New poll \"{title}\" created in #{context.channel} in {context.guild}: <{url}>\n```fix\nYou may have to refresh the page if the site says scripts are blocked.```")
        else:
            user = await get_or_fetch_user(self, self.dev_id)
            await user.send(f"New poll \"{title}\" created in #{context.channel} in {context.guild}: <{url}>\n```fix\nYou may have to refresh the page if the site says scripts are blocked.```")

    @commands.command(aliases=['currentpoll', 'cur'])
    @commands.guild_only()
    async def current(self, context):
        content = self.cur_results('The current poll is here: <[link]>')
        self.poll_message = await context.channel.send(content=content)
        if not self.should_update and self.poll['type'] == 'com' and not str.startswith(content, 'Error'):
            self.should_update = True
            try:
                self.result_updater.start()
            except:
                self.result_updater.restart()

    @commands.command()
    @commands.guild_only()
    async def end(self, context, silent=False):
        if self.poll is None:
            poll_file = open('savedata\\poll.json','r')
            self.poll = json.loads(poll_file.read())
            poll_file.close()

        if self.poll['type'] == 'com':
            if not silent:
                await context.channel.send(content=self.cur_results('**Ending the poll!**', ended=True))
            self.should_update = False
            resp = requests.post(url=self.com_delete_url, headers=self.headers, data=f'{{"content_id": "{self.poll["data"]["content_id"]}"}}')
            try:
                self.ended = True
                resp = resp.json()
                if resp['success']:
                    print('Poll delete ' + green('successful'))
                else:
                    print('Poll delete ' + red('unsuccessful'))
            except:
                print('Poll delete ' + red('ERROR'))
        else:
            await context.channel.send('Error: Cannot delete strawpoll.me polls')
