import discord
from discord.ext import commands
from bot.config import ROLE_TO_REMOVE

def setup(bot):
    @bot.event
    async def on_member_join(member: discord.Member):
        role = discord.Object(id=ROLE_TO_REMOVE)
        await member.add_roles(role)
