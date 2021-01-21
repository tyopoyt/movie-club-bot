import discord
import requests
import pprint
import json
from colorama import Fore
from datetime import datetime
from discord.ext import commands

class Strawpoll(commands.Cog):
    me_url = 'https://www.strawpoll.me/api/v2/polls'
    com_url = 'https://strawpoll.com/api/poll'
    com_delete_url = 'https://strawpoll.com/api/content/delete'
    pp = pprint.PrettyPrinter(depth=6)
    headers = {}

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot
        config_file = open('src\\config.json', 'r') 
        self.headers['API-KEY'] = json.loads(config_file.read())['auth']['com']
        authfile.close()

    def cur_results(self, prefix=''):
        poll_file = open('src\\poll.json','r')
        poll = json.loads(poll_file.read())
        poll_file.close()

        prefix = str(prefix).replace('[link]', poll['link'])

        message = prefix + "\n\n**Results:**\n```ini\n"
        highest = 0
        winners = []
        losers = []

        if poll['type'] == 'com':
            try:
                response = (requests.get(self.com_url + f"/{poll['data']['content_id']}").json())['content']
            except:
                print('Poll is' + Fore.RED + ' INVALID' + Fore.WHITE)
                return 'Error: Current poll is invalid'

            for answer in response['poll']['poll_answers']:
                if answer['votes'] > highest:
                    highest = answer['votes']
                    losers.extend(winners)
                    winners = [{'answer': answer['answer'], 'votes': answer['votes']}]
                elif answer['votes'] == highest:
                    winners.append({'answer': answer['answer'], 'votes': answer['votes']})
                else:
                    losers.append({'answer': answer['answer'], 'votes': answer['votes']})
            
            for answer in winners:
                message += f"[ {answer['answer']}: {answer['votes']} votes ]\n"

            for answer in losers:
                message += f"; {answer['answer']}: {answer['votes']} votes\n"

            message += f"```*(As of {datetime.now().strftime('%a, %b %d  %H:%M:%S')} ET)*"
        else:
            try:                
                response = requests.get(self.me_url + f"/{poll['data']['id']}").json()
                # TODO: format results from .me
                message += '```'
            except:
                message = 'Error: Could not retrieve poll from strawpoll.me'

        return message

    @commands.command()
    async def makepoll(self, context, arg='com'):
        poll = {}
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
            await context.channel.send(f'Genre poll for this week: {url}')

        elif arg == 'me':
            data = { "title": "Vote for a genre to watch", "options": ["Sci-Fi", "Comedy", "Action/Adventure",
                    "Horror", "Thriller", "Animated", "Drama", "Shitpost", "TV Show"], "multi": True, "captcha": True }
            response = requests.post(url=self.me_url, json=data)
            data = response.json()
            url = f'https://www.strawpoll.me/{data["id"]}/'
            await context.channel.send(f'Genre poll for this week: {url}')

        else:
            await context.channel.send(f'Unrecongnized poll site.  Options: {self.movie_bot.command_prefix}makepoll com or {self.movie_bot.command_prefix}makepoll me\n(Default is me)')
            return
        
        poll['type'] = arg
        poll['link'] = url
        poll['data'] = data
        poll_file = open('src\\poll.json','w')
        poll_file.write(json.dumps(poll))
        poll_file.close()

    @commands.command(aliases=['currentpoll', 'poll'])
    async def current(self, context):
        await context.channel.send(content=self.cur_results('The current poll is here: <[link]>'))

    @commands.command()
    async def end(self, context):
        poll_file = open('src\\poll.json','r')
        poll = json.loads(poll_file.read())
        poll_file.close()

        if poll['type'] == 'com':
            await context.channel.send(content=self.cur_results('**Ending the poll!**'))
            resp = requests.post(url=self.com_delete_url, headers=self.headers, data=f'{{"content_id": "{poll["data"]["content_id"]}"}}')
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


def setup(movie_bot):
    movie_bot.add_cog(Strawpoll(movie_bot))
