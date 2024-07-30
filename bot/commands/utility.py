import discord
from discord.ext import commands
import asyncio
import sys
import os

# Aggiungi il percorso del modulo config al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ROLE_TO_ADD, ROLE_TO_REMOVE

# Funzione per generare un codice CAPTCHA
def generate_captcha():
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Memoria dei CAPTCHA attivi
active_captchas = {}

def setup(bot):
    @bot.tree.command(name="verify", description="Verifica il tuo account con CAPTCHA")
    async def verify(interaction: discord.Interaction):
        user = interaction.user
        captcha_code = generate_captcha()
        active_captchas[user.id] = captcha_code

        await interaction.response.send_message(
            f"Per verificare il tuo account, rispondi a questo messaggio con il codice CAPTCHA: {captcha_code}. Hai 5 minuti per completare la verifica.",
            ephemeral=True
        )

        def check(m):
            return m.author == user and m.channel == interaction.channel and m.content == captcha_code

        try:
            msg = await bot.wait_for('message', check=check, timeout=300)
            await user.add_roles(discord.Object(id=ROLE_TO_ADD))
            await user.remove_roles(discord.Object(id=ROLE_TO_REMOVE))
            await interaction.followup.send("Verifica completata con successo!", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("Tempo scaduto. Verifica non completata.", ephemeral=True)
        finally:
            if user.id in active_captchas:
                del active_captchas[user.id]
import discord
from discord.ext import commands
from bot.utils import generate_unique_id, report_data, suggestion_data

ROLE_TO_ADD = 1247985624053452871
ROLE_TO_REMOVE = 1247604132047749242

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

   # aggiungi i tuoi comandi
        
def setup(bot):
    bot.add_cog(Utility(bot))
