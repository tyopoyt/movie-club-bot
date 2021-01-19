import discord
import requests
import pprint
from discord.ext import commands

class Strawpoll(commands.Cog):
    dot_me_url = 'https://www.strawpoll.me/api/v2/polls'
    dot_com_url = 'https://strawpoll.com/api/poll'
    pp = pprint.PrettyPrinter(depth=6)

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

    @commands.command()
    async def makepoll(self, context, arg='com'):
        if arg == 'me':
            data = { "title": "Vote for a genre to watch", "options": ["Sci-Fi", "Comedy", "Action/Adventure",
                    "Horror", "Thriller", "Animated", "Drama", "Shitpost", "TV Show"], "multi": True, "captcha": True }
            response = requests.post(url=self.dot_me_url, json=data)
            data = response.json()
            await context.channel.send(f'Genre poll for this week: https://www.strawpoll.me/{data["id"]}/')
        elif arg == 'com':
            data = { 
                     "poll": { 
                         "title": "Vote for a genre to watch",
                         "answers": ["Sci-Fi", "Comedy", "Action/Adventure",
                                     "Horror", "Thriller", "Animated", "Drama",
                                     "Shitpost", "TV Show"],
                         "ma": True
                         }
                    }
            response = requests.post(url=self.dot_com_url, json=data)
            data = response.json()
            await context.channel.send(f'Genre poll for this week: https://strawpoll.com/{data["content_id"]}/')
        else:
            await context.channel.send(f'Unrecongnized poll site.  Options: {self.movie_bot.command_prefix}makepoll com or {self.movie_bot.command_prefix}makepoll me\n(Default is me)')


def setup(movie_bot):
    movie_bot.add_cog(Strawpoll(movie_bot))
