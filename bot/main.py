import discord
from discord.ext import commands
import asyncio
import random
import string
import sys
import os

# Aggiungi la directory principale al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa le configurazioni
from config import TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Carica i moduli di comandi ed eventi
from commands import utility, moderation, report_suggestion, ticket

utility.setup(bot)
moderation.setup(bot)
report_suggestion.setup(bot)
ticket.setup(bot)

# Evento di quando il bot è pronto
@bot.event
async def on_ready():
    print(f'Siamo entrati come {bot.user}')
    await bot.tree.sync()
    print(f'Comandi slash sincronizzati')

bot.run(TOKEN)
