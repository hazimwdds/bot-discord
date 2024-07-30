import discord
from discord.ext import commands
from bot.config import TICKET_CHANNEL_ID, STAFF_ROLE_ID

def setup(bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        # Controllo anti-raid
        if message.channel.id == TICKET_CHANNEL_ID:
            staff_role = discord.utils.get(message.guild.roles, id=STAFF_ROLE_ID)
            if staff_role and staff_role not in message.author.roles:
                await message.delete()
                log_channel = discord.utils.get(message.guild.text_channels, name='log')
                if log_channel:
                    await log_channel.send(f'**ATTENZIONE**: Messaggio di {message.author.mention} bloccato nel canale {message.channel.mention}. Potenziale attacco di raid.')
