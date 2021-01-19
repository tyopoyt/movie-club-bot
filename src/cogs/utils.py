import discord
from discord.ext import commands

class Utilities(commands.Cog):
    def __init__(self, movie_bot):
        self.movie_bot = movie_bot

def setup(movie_bot):
    movie_bot.add_cog(Utilities(movie_bot))
