import discord
from discord.ext import commands

class Google(commands.Cog):
    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

def setup(movie_bot):
    movie_bot.add_cog(Google(movie_bot))
