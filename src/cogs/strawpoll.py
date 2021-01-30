import discord
import asyncio
import requests
import pprint
import json
from colorama import Fore
from datetime import datetime
from discord.ext import commands, tasks

def setup(movie_bot):
    movie_bot.add_cog(Strawpoll(movie_bot))

class Strawpoll(commands.Cog):
    me_url = 'https://www.strawpoll.me/api/v2/polls'
    com_url = 'https://strawpoll.com/api/poll'
    com_delete_url = 'https://strawpoll.com/api/content/delete'
    pp = pprint.PrettyPrinter(depth=6)
    headers = {}
    should_update = False
    timing_task = None
    movie_bot = None
    poll_message = None
    poll = None

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot
        config_file = open('src\\config.json', 'r') 
        self.headers['API-KEY'] = json.loads(config_file.read())['auth']['com']
        config_file.close()

    # check the results of current poll and return a string that can be sent on discord
    def cur_results(self, prefix='', ended=False):
        if self.poll is None:
            poll_file = open('src\\poll.json','r')
            self.poll = json.loads(poll_file.read())
            poll_file.close()

        prefix = str(prefix).replace('[link]', self.poll['link'])

        message = prefix + f"\n\n**{'Final ' if ended else ''}Results:**\n```ini\n"
        highest = 0
        winners = []
        losers = []

        if self.poll['type'] == 'com':
            try:
                response = (requests.get(self.com_url + f"/{self.poll['data']['content_id']}").json())['content']
            except:
                print('Poll is' + Fore.RED + ' INVALID' + Fore.WHITE)
                return 'Error: Current poll is invalid (Has it been ended?)'

            # check results of the poll
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
        await self.poll_message.edit(content=self.cur_results(self.poll_message.content[0:self.poll_message.content.find('\n\n**Results:**')]))
        await asyncio.sleep(self.result_updater.seconds)


    @commands.command()
    async def makepoll(self, context, arg='com'):
        self.poll = {}
        url = ''

        if arg == 'com':
            data = { 
                     "poll": { 
                         "title": "Vote for a genre to watch",
                         "answers": ["Sci-Fi", "Comedy", "Action/Adventure",
                                     "Horror", "Thriller", "Animated", "Drama",
                                     "Shitpost", "TV Show"],
                         "ma": True
                         }
                    }
            response = requests.post(url=self.com_url, json=data, headers=self.headers)
            data = response.json()
            url = f'https://strawpoll.com/{data["content_id"]}/'

            self.poll['type'] = arg
            self.poll['link'] = url
            self.poll['data'] = data

            self.poll_message = await context.channel.send(self.cur_results(f'Genre poll for this week: <{url}>'))

            if not self.should_update:
                self.should_update = True
                self.result_updater.start()

        elif arg == 'me':
            data = { "title": "Vote for a genre to watch", "options": ["Sci-Fi", "Comedy", "Action/Adventure",
                    "Horror", "Thriller", "Animated", "Drama", "Shitpost", "TV Show"], "multi": True, "captcha": True }
            response = requests.post(url=self.me_url, json=data)
            data = response.json()
            url = f'https://www.strawpoll.me/{data["id"]}/'

            self.poll['type'] = arg
            self.poll['link'] = url
            self.poll['data'] = data

            self.poll_message = await context.channel.send(f'Genre poll for this week: {url}')

        else:
            await context.channel.send(f'Unrecongnized poll site.  Options: {self.movie_bot.command_prefix}makepoll com or {self.movie_bot.command_prefix}makepoll me\n(Default is me)')
            return

        poll_file = open('src\\poll.json','w')
        poll_file.write(json.dumps(self.poll))
        poll_file.close()

    @commands.command(aliases=['currentpoll', 'cur'])
    async def current(self, context):
        content = self.cur_results('The current poll is here: <[link]>')
        self.poll_message = await context.channel.send(content=content)
        if not self.should_update and self.poll['type'] == 'com' and not str.startswith(content, 'Error'):
            self.should_update = True
            self.result_updater.start()

    @commands.command()
    async def end(self, context):
        if self.poll is None:
            poll_file = open('src\\poll.json','r')
            self.poll = json.loads(poll_file.read())
            poll_file.close()

        if self.poll['type'] == 'com':
            await context.channel.send(content=self.cur_results('**Ending the poll!**', ended=True))
            self.should_update = False
            resp = requests.post(url=self.com_delete_url, headers=self.headers, data=f'{{"content_id": "{self.poll["data"]["content_id"]}"}}')
            try:
                resp = resp.json()
                if resp['success']:
                    print('Poll delete' + Fore.GREEN + ' successful' + Fore.WHITE)
                else:
                    print('Poll delete' + Fore.RED + ' unsuccessful' + Fore.WHITE)
            except:
                print('Poll delete' + Fore.RED + ' ERROR' + Fore.WHITE)
        else:
            await context.channel.send('Error: Cannot delete strawpoll.me polls')
