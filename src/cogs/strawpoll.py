import discord
import requests
import pprint
from discord.ext import commands

class Strawpoll(commands.Cog):
    url = 'https://www.strawpoll.me/api/v2/polls'
    pp = pprint.PrettyPrinter(depth=6)

    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

    @commands.command()
    async def makepoll(self, context):
        # data = { "title": "This is a test poll.", "options": ["Option #1", "Option #2"], "multi": True }
        # response = requests.post(url=self.url, json=data)
        # data = response.json()
        # print(data)
        return

def setup(movie_bot):
    movie_bot.add_cog(Strawpoll(movie_bot))
