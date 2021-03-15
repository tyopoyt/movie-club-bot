import discord

async def get_or_fetch_user(self, user_id):
    user = self.movie_bot.get_user(user_id)
    if user is None:
        user = await self.movie_bot.fetch_user(user_id)
    return user